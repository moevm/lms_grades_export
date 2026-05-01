import argparse


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client_id", type=str, required=True, help="app for stepic access")
    parser.add_argument("--client_secret", type=str, required=True, help="key for stepic access")
    parser.add_argument("--course_id", type=str, required=True, help="id of the course")
    parser.add_argument("--class_id", type=str, required=False, help="id of the class in the course")
    parser.add_argument("--csv_path", type=str, required=True, help="Specify path to output csv file")
    parser.add_argument(
        '--yandex_token',
        type=str,
        required=False,
        help='Specify Yandex token from https://oauth.yandex.ru/client/new application',
    )
    parser.add_argument('--yandex_path', type=str, required=False, help='Specify output filename on Yandex Disk')
    args = parser.parse_args()
    return args
