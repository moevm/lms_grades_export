import argparse


def arg_parser_dis():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--google_token",
        type=str,
        required=False,
        default="conf.json",
        help="Specify path to google token file",
    )
    parser.add_argument(
        "--checker_token",
        type=str,
        required=True,
        help="Specify session cookie for slides-checker",
    )
    parser.add_argument(
        "--checker_filter",
        type=str,
        required=False,
        help="Specify filter for slides-checker",
    )
    parser.add_argument(
        "--table_id",
        type=str,
        required=False,
        help="Specify Google sheet document id (can find in url)",
    )
    parser.add_argument(
        "--sheet_name",
        type=str,
        required=False,
        help="Specify title for a sheet in a document in which data will be printed",
    )
    parser.add_argument(
        "--sheet_id",
        type=str,
        required=False,
        help="Specify ID for a sheet in a document in which data will be printed. If set, sheet_name is ignored",
    )
    parser.add_argument(
        "--yandex_token",
        type=str,
        required=False,
        help="Specify Yandex token from https://oauth.yandex.ru/client/new application",
    )
    parser.add_argument(
        "--yandex_path",
        type=str,
        required=False,
        help="Specify output filename on Yandex Disk",
    )
    args = parser.parse_args()
    return args


def arg_parser_moodle():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--moodle_token", type=str, required=True, help="Specify moodle token"
    )
    parser.add_argument("--url", type=str, required=True, help="url of the platform")
    parser.add_argument(
        "--course_id",
        type=lambda s: [i for i in s.split(",")],
        required=True,
        help="Id of a course to parse",
    )
    parser.add_argument(
        "--csv_path", type=str, required=True, help="Specify path to output csv file"
    )
    parser.add_argument(
        "--google_token",
        type=str,
        required=False,
        help="Specify path to google token file",
    )
    parser.add_argument(
        "--table_id",
        type=lambda s: [i for i in s.split(",")],
        required=False,
        help="Specify Google sheet document id (can find in url)",
    )
    parser.add_argument(
        "--sheet_name",
        type=lambda s: [i for i in s.split(",")],
        required=False,
        help="Specify title for a sheet in a document in which data will be printed",
    )
    parser.add_argument(
        "--sheet_id",
        type=lambda s: [i for i in s.split(",")],
        required=False,
        help="Specify ID for a sheet in a document in which data will be printed. If set, sheet_name is ignored",
    )
    parser.add_argument(
        "--yandex_token",
        type=str,
        required=False,
        help="Specify Yandex token from https://oauth.yandex.ru/client/new application",
    )
    parser.add_argument(
        "--yandex_path",
        type=str,
        required=False,
        help="Specify output filename on Yandex Disk",
    )
    parser.add_argument(
        "--percentages",
        required=False,
        action="store_true",
        help="If set then grades will be printed as percentages",
    )
    parser.add_argument(
        "--options",
        type=lambda s: set(i for i in s.split(",")),
        required=False,
        help="Specify options for column names",
    )
    args = parser.parse_args()
    return args


def arg_parser_stepik():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--client_id", type=str, required=True, help="app for stepic access"
    )
    parser.add_argument(
        "--client_secret", type=str, required=True, help="key for stepic access"
    )
    parser.add_argument("--url", type=str, required=True, help="url of the platform")
    parser.add_argument("--course_id", type=str, required=True, help="id of a course")
    parser.add_argument(
        "--class_id", type=str, required=False, help="id of class in this course"
    )
    parser.add_argument(
        "--csv_path", type=str, required=True, help="Specify path to output csv file"
    )
    parser.add_argument(
        "--google_token",
        type=str,
        required=False,
        help="Specify path to google token file",
    )
    parser.add_argument(
        "--table_id",
        type=str,
        required=False,
        help="Specify Google sheet document id (can find in url)",
    )
    parser.add_argument(
        "--sheet_name",
        type=str,
        required=False,
        help="Specify title for a sheet in a document in which data will be printed",
    )
    parser.add_argument(
        "--sheet_id",
        type=str,
        required=False,
        help="Specify ID for a sheet in a document in which data will be printed. If set, sheet_name is ignored",
    )
    parser.add_argument(
        "--yandex_token",
        type=str,
        required=False,
        help="Specify Yandex token from https://oauth.yandex.ru/client/new application",
    )
    parser.add_argument(
        "--yandex_path",
        type=str,
        required=False,
        help="Specify output filename on Yandex Disk",
    )
    args = parser.parse_args()
    return args
