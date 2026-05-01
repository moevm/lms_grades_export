from datetime import datetime

import numpy as np
import pandas as pd
import requests
import yadisk
from args_parser import arg_parser
from tqdm import tqdm


def get_access_token(client_id, client_secret):
    response = requests.post(
        "https://stepik.org/oauth2/token/",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    data = response.json()
    return data["access_token"]


def get_grade_list(access_token, course_id, class_id):
    results = []
    page = 1
    with tqdm(desc="Grade list") as t:
        while True:
            response = requests.get(
                "https://stepik.org/api/course-grades",
                params={
                    "page": page,
                    "page_size": 10,
                    "course": course_id,
                    "klass": class_id,
                },
                headers={"Authorization": f"BEARER {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            results.extend(data["course-grades"])
            if not data["meta"]["has_next"]:
                break
            t.update()
            page += 1

    return results


def get_submissions(access_token, class_id, step_id, user_id):
    page = 1
    results = []
    while True:
        response = requests.get(
            "https://stepik.org/api/submissions",
            params={
                "page": page,
                "page_size": 10,
                "klass": class_id,
                "order": "desc",
                "step": step_id,
                "search": f"id:{user_id}",
            },
            headers={"Authorization": f"BEARER {access_token}"},
        )
        response.raise_for_status()
        data = response.json()
        results.extend(data["submissions"])
        if not data["meta"]["has_next"]:
            break
        page += 1
    return results


def get_step_ids(data):
    steps_ids = []

    for datum in data:
        for step_datum in datum["results"].values():
            steps_ids.append(step_datum["step_id"])

    return sorted(list(set(steps_ids)))


def get_info(access_token, course_id, class_id):
    data = get_grade_list(access_token=access_token, course_id=course_id, class_id=class_id)
    step_ids = get_step_ids(data)

    is_read = {}

    # data = data[:2]

    # if os.path.exists("res.csv"):
    #     df = pd.read_csv("res.csv")
    #     for _, datum in df.iterrows():
    #         user_id = datum["user_id"]
    #         for step_id in step_ids:
    #             if not pd.isna(datum.get(str(step_id), None)):
    #                 is_read[f"{user_id}-{step_id}"] = datum.get(str(step_id))

    # print(is_read)

    results = []
    for i in range(len(data)):
        datum = data[i]
        user_id = datum["user"]
        print(f"user_id: {user_id} [{i} / {len(data)}]")

        user_datum = {
            "user_id": user_id,
            "score": datum["score"],
            "date_joined": datum["date_joined"],
        }

        for result in tqdm(list(datum["results"].values())):
            step_id = result["step_id"]
            key = f"{user_id}-{step_id}"
            if key in is_read:
                user_datum[str(step_id)] = is_read[key]
                continue
            submissions = get_submissions(
                access_token=access_token,
                class_id=class_id,
                step_id=step_id,
                user_id=user_id,
            )
            for submission in submissions:
                if submission["status"] == "correct":
                    user_datum[str(step_id)] = submission["time"]
                    break
        results.append(user_datum)

    df = pd.DataFrame(
        results,
        columns=["user_id", "score", "date_joined", *[str(id_) for id_ in step_ids]],
    )

    return df


def postprocess_df(df):
    new_df = df.copy(deep=True)
    for column in new_df.columns[3:]:
        new_df[column] = new_df[column].fillna("").apply(lambda d: d[:10])

    start_date = new_df.apply(lambda item: np.min(item[3:]), axis=1)
    end_date = new_df.apply(lambda item: np.max(item[3:]), axis=1)
    uniq_dates = new_df.apply(lambda item: len(np.unique(item[3:])), axis=1)
    days = new_df.apply(
        lambda item: (
            (datetime.strptime(np.max(item[3:]), "%Y-%m-%d") - datetime.strptime(np.min(item[3:]), "%Y-%m-%d")).days
        ),
        axis=1,
    )
    new_df["uniq_dates"] = uniq_dates
    new_df["start_date"] = start_date
    new_df["end_date"] = end_date
    new_df["days"] = days
    new_df["date_joined"] = new_df["date_joined"].apply(lambda d: d[:10])
    new_df = new_df[
        [
            *new_df.columns[:3],
            "uniq_dates",
            "start_date",
            "end_date",
            "days",
            *new_df.columns[3:-2],
        ]
    ]

    return new_df


def load_to_yandex_disk(csv_path, dest_path, token):
    try:
        client = yadisk.YaDisk(token=token)
        client.upload(csv_path, dest_path)
        print(f'Check data in your disk! Path to the table is: {dest_path}')
    except Exception as e:
        print(f'Saving data to Yandex Disk failed. Error message: {e}')
        return


if __name__ == "__main__":
    args = arg_parser()
    token = get_access_token(client_id=args.client_id, client_secret=args.client_secret)
    df = get_info(access_token=token, course_id=args.course_id, class_id=args.class_id)
    new_df = postprocess_df(df)
    new_df.to_csv(args.csv_path, index=False)
    if args.yandex_token and args.yandex_path:
        load_to_yandex_disk(args.csv_path, args.yandex_path, args.yandex_token)
