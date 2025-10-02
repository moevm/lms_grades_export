import argparse


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client_id', type=str, required=True, help='app for stepic access')
    parser.add_argument('--client_secret', type=str, required=True, help='key for stepic access')
    parser.add_argument('--url', type=str, required=True, help='url of the platform')
    parser.add_argument('--course_id', type=str, required=True, help='id of a course')
    parser.add_argument('--class_id', type=str, required=False, help='id of class in this course')
    parser.add_argument('--csv_path', type=str, required=True, help='Specify path to output csv file')
    parser.add_argument('--google_token', type=str, required=False, help='Specify path to google token file')
    parser.add_argument('--table_id', type=str, required=False, help='Specify Google sheet document id (can find in url)')
    parser.add_argument('--sheet_name', type=str, required=False, help='Specify title for a sheet in a document in which data will be printed')
    parser.add_argument('--sheet_id', type=str, required=False, help='Specify ID for a sheet in a document in which data will be printed. If set, sheet_name is ignored')
    parser.add_argument('--yandex_token', type=str, required=False, help='Specify Yandex token from https://oauth.yandex.ru/client/new application')
    parser.add_argument('--yandex_path', type=str, required=False, help='Specify output filename on Yandex Disk')
    args = parser.parse_args()
    return args

