#!/usr/bin/python3
import datetime
import json
import re

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from utils.arg_parser import arg_parser_moodle
from utils.gspread import write_data_to_table

HEADERS = {"Content-Type": "charset=iso-8859"}


class Main:
    args = None
    skip_item_classes = {"category"}
    item_class = "column-itemname"
    level1_class = "level1"

    @staticmethod
    def extract_grade_from_html(html_content):
        if not html_content or html_content == "-":
            return "-"
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            matches = re.findall(r'\d+,\d+', text)
            if matches:
                return matches[0]
            matches_int = re.findall(r'\d+', text)
            if matches_int:
                return matches_int[0] + ",0"
            return "-"
        except Exception:
            return "-"

    @classmethod
    def parse_person_table(cls, data, users_params):
        def to_float_from_comma(x):
            return float(x.replace(",", ".")) if x != "-" else "-"

        grades_data = []
        for person in data:
            user_id = person["userid"]
            person_grades = dict(
                userid=user_id,
                userfullname=person["userfullname"],
                activities=[],
                **users_params[str(user_id)],
            )
            if cls.args.options and "github" in cls.args.options:
                person_grades["github"] = users_params[str(user_id)]["github"]

            for row in person["tabledata"]:
                if "leader" in row:
                    continue
                if "itemname" not in row:
                    continue

                item = row["itemname"]
                classes = set(item.get("class", "").split())

                if cls.skip_item_classes & classes:
                    continue

                is_total = cls.level1_class in classes  # level1

                if is_total:
                    activity_name = "total"
                    activity_id = None
                    grade_content = row["grade"]["content"]
                    if grade_content == "-":
                        grade_content = "0,0"
                        row["percentage"]["content"] = "0,0 %"
                    grade = cls.extract_grade_from_html(row["grade"]["content"])
                    percentage = to_float_from_comma(row["percentage"]["content"].split(" ")[0])
                    contribution = row["contributiontocoursetotal"]["content"]
                else:
                    html_content = item["content"]
                    soup = BeautifulSoup(html_content, "html.parser")

                    link = soup.find("a", class_="gradeitemheader")
                    if link:
                        activity_name = link.get_text(strip=True)
                        href = link.get("href", "")
                        match = re.search(r"[?&]id=(\d+)", href)
                        activity_id = match.group(1) if match else None
                    else:
                        title_span = soup.find("span", class_="rowtitle")
                        activity_name = title_span.get_text(strip=True) if title_span else soup.get_text(strip=True)
                        activity_id = None

                    grade = cls.extract_grade_from_html(row["grade"]["content"])
                    percentage = to_float_from_comma(row["percentage"]["content"].split(" ")[0])
                    contribution = row["contributiontocoursetotal"]["content"]

                person_grades["activities"].append(
                    {
                        "activity_name": activity_name,
                        "activity_id": activity_id,
                        "grade": grade,
                        "percentage": percentage,
                        "contributiontocoursetotal": contribution,
                    }
                )

            grades_data.append(person_grades)

        return grades_data

    @classmethod
    def main(cls):
        cls.args = arg_parser_moodle()
        for course_id in cls.args.course_id:
            with requests.Session() as s:
                # get enrolled users
                res_users = s.get(
                    f"{cls.args.url}/webservice/rest/server.php?wstoken={cls.args.moodle_token}"
                    f"&wsfunction=core_enrol_get_enrolled_users&courseid={course_id}&moodlewsrestformat=json&moodlewssettinglang=ru",
                    headers=HEADERS,
                )
                # check status code
                if res_users.status_code != 200:
                    raise SystemExit("Request error, response status code: " + str(res_users.status_code))

                users = json.loads(res_users.text)
                # check if request is valid
                if not isinstance(users, list):
                    raise SystemExit("Error: " + users["message"])

                # save last accessed time for each user
                users_params = {}
                for item in users:
                    users_params[str(item["id"])] = {
                        "last_access": datetime.datetime.fromtimestamp(item["lastcourseaccess"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "username": item.get("username", "-"),
                        "email": item.get("email", "-"),
                    }
                    users_params[str(item["id"])]["github"] = (
                        item["customfields"][0].get("value", "-") if "customfields" in item else "-"
                    )

                # get grades
                res_grades = s.get(
                    f"{cls.args.url}/webservice/rest/server.php?wstoken={cls.args.moodle_token}"
                    f"&wsfunction=gradereport_user_get_grades_table&courseid={course_id}&moodlewsrestformat=json&moodlewssettinglang=ru",
                    headers=HEADERS,
                )

                # check status code
                if res_grades.status_code != 200:
                    raise SystemExit("Request error, response status code: " + str(res_grades.status_code))

                grades = json.loads(res_grades.text)

                # check if request is valid
                if "message" in grades:
                    raise SystemExit("Error: " + grades["message"])

                # parse grades data
                grades_data = cls.parse_person_table(grades["tables"], users_params)

                if len(grades_data) == 0:
                    print("No solutions in course, nothing to export. Exiting")
                    return

                # form suitable structure for output to sheets
                grades_for_table = []
                grades_type = "grade"
                if cls.args.percentages:
                    grades_type = "percentage"

                for item in grades_data:
                    person_grades = {}
                    person_grades["fullname"] = item["userfullname"]
                    person_grades["username"] = item["username"]
                    person_grades["email"] = item["email"]
                    if cls.args.options and "github" in cls.args.options:
                        person_grades["github"] = item["github"]
                    person_grades["last_access"] = item["last_access"]
                    for activity in item["activities"]:
                        item_name = (
                            f"{activity['activity_name']} (id={activity['activity_id']})"
                            if activity["activity_id"]
                            else activity["activity_name"]
                        )
                        person_grades[item_name] = activity[grades_type]  # issue #30
                    grades_for_table.append(person_grades)

                df = DataFrame(grades_for_table)

                # output data to csv file
                csv_path = f"{cls.args.csv_path}_{course_id}.csv"
                df.to_csv(csv_path, sep=";", decimal=",", encoding="UTF-8")

                # if cls.args specified write data to sheets document
                if cls.args.google_token and cls.args.table_id:
                    for i in range(0, len(cls.args.table_id)):
                        if cls.args.course_id[i] == course_id:
                            table_id = cls.args.table_id[i]
                            break
                        elif i == len(cls.args.table_id) - 1:
                            table_id = cls.args.table_id[i]

                    if cls.args.sheet_id:
                        write_data_to_table(
                            df,
                            cls.args.google_token,
                            table_id,
                            sheet_id=cls.args.sheet_id[0],
                        )
                        print(f"writed to {table_id} {cls.args.sheet_id[0]}")
                    else:
                        if cls.args.sheet_name:
                            for i in range(0, len(cls.args.sheet_name)):
                                if cls.args.course_id[i] == course_id:
                                    sheet_name = cls.args.sheet_name[i]
                                    break
                                else:
                                    sheet_name = cls.args.sheet_name[i] + " " + course_id
                        else:
                            sheet_name = "course " + course_id
                        write_data_to_table(df, cls.args.google_token, table_id, sheet_name=sheet_name)
                print(f"End exporting for course_id={course_id}")

                # write data to yandex disk
                if cls.args.yandex_token and cls.args.yandex_path:
                    # TODO: refactor нadisk
                    from utils.yandex_disk import write_sheet_to_file

                    write_sheet_to_file(
                        cls.args.yandex_token,
                        cls.args.yandex_path,
                        csv_path,
                        sheet_name="Онлайн-курс",
                    )

                    yandex_path = cls.args.yandex_path
                    print(f"Course {cls.args.course_id} uploaded to table on Disk! Path to the table is: {yandex_path}")


if __name__ == "__main__":
    Main.main()
