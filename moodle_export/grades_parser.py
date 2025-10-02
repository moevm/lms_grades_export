#!/usr/bin/python3
import sheets
import requests
import json
import datetime
import args_parser
import logging
import sys
from pandas import DataFrame

HEADERS = {"Content-Type": "charset=iso-8859"}


class Main:
    args = None
    skip_item_classes = {"category"}
    item_class = "column-itemname"
    level1_class = "level1"

    @classmethod
    def parse_person_table(cls, data, users_params):
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

            #print(f'userid: {user_id} fullname: {person_grades["userfullname"]}')

            for activity in person["tabledata"]:
                itemname_key = "itemname"
                if type(activity) == dict and itemname_key in activity:
                    item_classes = set(activity[itemname_key].get("class").split(" "))

                    # if item has skipped class -> go to next item
                    if cls.skip_item_classes & item_classes:
                        continue
                    activity_id = None
                    # if item has class 'leve1' -> it's Course total (we hope)
                    if cls.level1_class not in item_classes:
                        activity_name_raw_content = activity[itemname_key][
                            "content"
                        ]  # html
                        activity_name = activity_name_raw_content.rpartition("</a>")[
                            0
                        ].rsplit('">')[-1]
                        activity_id = activity[itemname_key]["id"].split("_")[1]
                        activity["grade"]["content"] = activity["grade"][
                            "content"
                        ].rsplit(">", 1)[-1]
                    else:
                        activity_name = "total"
                        if activity["grade"]["content"] == "-":
                            activity["grade"]["content"] = "0,0"  # issue #13
                        activity["percentage"]["content"] = "0,0 %"

                    #print(activity_name)

                    to_float_from_comma = lambda x: (
                        float(x.replace(",", ".")) if x != "-" else "-"
                    )

                    person_grades["activities"].append(
                        {
                            "activity_name": activity_name,
                            "activity_id": activity_id,
                            "grade": to_float_from_comma(activity["grade"]["content"]),
                            "percentage": to_float_from_comma(
                                activity["percentage"]["content"].split(" ")[0]
                            ),
                            "contributiontocoursetotal": activity[
                                "contributiontocoursetotal"
                            ][
                                "content"
                            ],  # ????
                        }
                    )

            grades_data.append(person_grades)

        return grades_data

    @classmethod
    def main(cls):
        cls.args = args_parser.arg_parser()
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
                    raise SystemExit(
                        "Request error, response status code: "
                        + str(res_users.status_code)
                    )

                users = json.loads(res_users.text)
                # check if request is valid
                if type(users) != list:
                    raise SystemExit("Error: " + users["message"])

                # save last accessed time for each user
                users_params = {}
                for item in users:
                    users_params[str(item["id"])] = {
                        "last_access": datetime.datetime.fromtimestamp(
                            item["lastcourseaccess"]
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "username": item.get("username", "-"),
                        "email": item.get("email", "-"),
                    }
                    users_params[str(item["id"])]["github"] = (
                        item["customfields"][0].get("value", "-")
                        if "customfields" in item
                        else "-"
                    )

                # get grades
                res_grades = s.get(
                    f"{cls.args.url}/webservice/rest/server.php?wstoken={cls.args.moodle_token}"
                    f"&wsfunction=gradereport_user_get_grades_table&courseid={course_id}&moodlewsrestformat=json&moodlewssettinglang=ru",
                    headers=HEADERS,
                )

                # check status code
                if res_grades.status_code != 200:
                    raise SystemExit(
                        "Request error, response status code: "
                        + str(res_grades.status_code)
                    )

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
                        sheets.write_data_to_table(
                            df,
                            cls.args.google_token,
                            table_id,
                            sheet_id=cls.args.sheet_id[0],
                        )
                        print(f'writed to {table_id} {cls.args.sheet_id[0]}')
                    else:
                        if cls.args.sheet_name:
                            for i in range(0, len(cls.args.sheet_name)):
                                if cls.args.course_id[i] == course_id:
                                    sheet_name = cls.args.sheet_name[i]
                                    break
                                else:
                                    sheet_name = (
                                        cls.args.sheet_name[i] + " " + course_id
                                    )
                        else:
                            sheet_name = "course " + course_id
                        sheets.write_data_to_table(
                            df, cls.args.google_token, table_id, sheet_name=sheet_name
                        )
                print(f"End exporting for course_id={course_id}")

                # write data to yandex disk
                if cls.args.yandex_token and cls.args.yandex_path:
                    # TODO: refactor нadisk
                    from utils import write_sheet_to_file

                    write_sheet_to_file(
                        cls.args.yandex_token,
                        cls.args.yandex_path,
                        csv_path,
                        sheet_name="Онлайн-курс",
                    )

                    yandex_path = cls.args.yandex_path
                    print(
                        f"Course {cls.args.course_id} uploaded to table on Disk! Path to the table is: {yandex_path}"
                    )


if __name__ == "__main__":
    Main.main()
