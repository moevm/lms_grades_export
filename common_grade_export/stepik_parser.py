# Run with Python 3
import sheets
import args_parser
import json
import requests
import csv
import yadisk
import logging
import sys


ALL_TASK_IDS = set()

# check status code and if request is valid
def check_access(response):
    if response.status_code != 200:
        raise SystemExit("Request error, response status code: " + str(response.status_code))

    data = json.loads(response.text)

    if "detail" in data:
        raise SystemExit("Error: " + response["detail"])
    return data


# Sort steps in actual order
def sort_steps(lesson, results):
    steps = []
    sorted_steps = []
    for key in results.keys():
        if lesson != key.split('-')[0]:
            sorted_steps += (i for i in sorted(steps, key=lambda x: x.split('-')[1]))
            lesson = key.split('-')[0]
            steps = []
        steps.append(key)
    sorted_steps += (i for i in sorted(steps, key=lambda x: x.split('-')[1]))
    return sorted_steps


# Get info from server answer
def parse_grades(user, url, token, sorted_steps):
    user_meta = requests.get(url + '/users/' + str(user['user']),
                             headers={'Authorization': 'Bearer ' + token})
    user_data = check_access(user_meta)
    full_name = user_data['users'][0]['full_name']
    if user.get("last_viewed") is None:
        last_viewed = "Never"
    else:
        last_viewed = user['last_viewed'][:10] + ' ' + user['last_viewed'][11:16]
    grades = ({'user id': user['user'], 'full name': full_name, 'last viewed': last_viewed, 'total score': user['score']})

    if user['results']:
        lesson = list(user['results'].keys())[0].split('-')[0]
    else:
        #print("No results for user ", user['id'])
        lesson = []

    if sorted_steps == []:
        sorted_steps = sort_steps(lesson, user['results'])

    for i in sorted_steps:
        key = user['results'][i]['step_id']
        grades.update({key: user['results'][i]['score']})
        global ALL_TASK_IDS
        ALL_TASK_IDS.add(key)
    return grades


def main():
    args = args_parser.arg_parser()
    sorted_steps = []
    grades_for_table = []
    page = 1

    # Get a token
    auth = requests.auth.HTTPBasicAuth(args.client_id, args.client_secret)
    response = requests.post('https://stepik.org/oauth2/token/',
                             data={'grant_type': 'client_credentials'},
                             auth=auth)
    token = response.json().get('access_token', None)
    if not token:
        print('Unable to authorize with provided credentials')
        exit(1)
    else:
        #logger.debug('********************************************************')
        print(f'stepik_export: Authorization valid')

    # get grades data
    if args.class_id:
        grades_meta = requests.get(args.url + '/course-grades?course=' + args.course_id + '&klass=' + args.class_id,
                        headers={'Authorization': 'Bearer ' + token})
        course_grades = check_access(grades_meta)
    else: # get grades data $$$
        grades_meta = requests.get(args.url + '/course-grades?course=' + args.course_id + '&page=' + str(page),
                                   headers={'Authorization': 'Bearer ' + token})
        course_grades = check_access(grades_meta)

    # Parse grades
    all_task_id = set()
    while True:
        if course_grades['course-grades']:
            #print(f'Parse {page} page')
            for user in course_grades['course-grades']:
                grades = parse_grades(user, args.url, token, sorted_steps)
                grades_for_table.append(grades)
                all_task_id.update(grades.keys())    # save all task id from student
            #print('Parsed!')

            if course_grades['meta']['has_next']:
                page += 1
                if args.class_id:
                    grades_meta = requests.get(
                        args.url + '/course-grades?course=' + args.course_id + '&klass=' + args.class_id + '&page=' + str(page),
                        headers={'Authorization': 'Bearer ' + token})
                else:
                    grades_meta = requests.get(
                        args.url + '/course-grades?course=' + args.course_id + '&page=' + str(page),
                        headers={'Authorization': 'Bearer ' + token})
                course_grades = check_access(grades_meta)
            else:
                #logger.debug('Well done! Start converting')
                break
        else:
            #print("stepik_export: no course_grades['course-grades']")
            break
            exit(1)

    # output data to csv file
    csv_path = args.csv_path + '_' + args.course_id + '.csv'
    with open(csv_path, 'w', encoding='UTF8', newline='') as f:
        global ALL_TASK_IDS
        fields = ['user id', 'full name', 'last viewed', 'total score'] + list(ALL_TASK_IDS)
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(grades_for_table)
    #print(f'Saved to csv file: {csv_path}')

    # write data to sheets document
    if args.google_token and args.table_id:
        #logger.debug('Send data to Google Sheets')
        if args.sheet_id:
            sheets.write_data_to_table(csv_path, args.google_token, args.table_id, sheet_id=args.sheet_id)
            print(f'Check data in your table! List id is: {args.sheet_id}')
        else:
            if args.sheet_name:
                sheet_name = args.sheet_name
            else:
                sheet_name = 'course ' + args.course_id
            sheets.write_data_to_table(csv_path, args.google_token, args.table_id, sheet_name=sheet_name)
            #logger.info(f'Check data in your table! List name is: {sheet_name}')
        #logger.debug('********************************************************')
    
    # write data to yandex disk
    if args.yandex_token and args.yandex_path:
        yandex_path = args.yandex_path + '_' + args.course_id + '.csv'
        try:
            client = yadisk.YaDisk(token=args.yandex_token)
            client.upload(csv_path, yandex_path)
            #logger.info(f'Check data in your disk! Path to the table is: {yandex_path}')
            #logger.debug('********************************************************')
        except Exception as e:
            #logger.error(f'Saving data to Yandex Disk failed. Error message: {e}')
            exit(1)

if __name__ == "__main__":
    main()
