import argparse
import csv
import json
import subprocess
import time

import httpx
import pandas

import sheets


def get_name(user_id: str, curl_args, rec_limit=10):
    try:
        if type(user_id) != str or user_id.isdigit():
            status, output = subprocess.getstatusoutput(
                f'''curl 'https://developerprofiles-pa.clients6.google.com/$rpc/google.internal.developerprofiles.v1.profile.ProfileService/GetPublicProfile' --compressed -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'X-Goog-Api-Key: AIzaSyAP-jjEJBzmIyKR4F-3XITp8yM9T1gEEI8' -H 'X-Goog-AuthUser: 0' -H 'Authorization: ' -H 'Content-Type: application/json+protobuf' -H 'X-User-Agent: grpc-web-javascript/0.1' -H 'Origin: https://developers.google.com' -H 'DNT: 1' -H 'Sec-GPC: 1' -H 'Connection: keep-alive' -H 'Referer: https://developers.google.com/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-site' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'TE: trailers' -s --data-raw '["{user_id}"]' '''
            )
        else:
            status, output = subprocess.getstatusoutput(
                f'''curl 'https://developerprofiles-pa.clients6.google.com/$rpc/google.internal.developerprofiles.v1.profile.ProfileService/GetPublicProfile'  --compressed -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'X-Goog-Api-Key: {curl_args}' -H 'X-Goog-AuthUser: 0' -H 'Authorization: ' -H 'Content-Type: application/json+protobuf' -H 'X-User-Agent: grpc-web-javascript/0.1' -H 'Origin: https://developers.google.com' -H 'DNT: 1' -H 'Sec-GPC: 1' -H 'Connection: keep-alive' -H 'Referer: https://developers.google.com/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-site' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -s --data-raw '[null,null,"{user_id}"]' '''
            )  # curl because libs don't work
        user_id = json.loads(
            output
        )
        user_id = user_id[1][4][0]
        return user_id
    except httpx.ConnectError:
        if rec_limit == 0:
            print('ConnectError')
            return ""
        time.sleep(0.1)
        return get_name(user_id, curl_args, rec_limit-1)
    return ""

def get_link(user_id: str, curl_args, rec_limit=10):
    try:
        if type(user_id) != str or user_id.isdigit():
            status, output = subprocess.getstatusoutput(
                f'''curl 'https://developerprofiles-pa.clients6.google.com/$rpc/google.internal.developerprofiles.v1.profile.ProfileService/GetPublicProfile' --compressed -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'X-Goog-Api-Key: AIzaSyAP-jjEJBzmIyKR4F-3XITp8yM9T1gEEI8' -H 'X-Goog-AuthUser: 0' -H 'Authorization: ' -H 'Content-Type: application/json+protobuf' -H 'X-User-Agent: grpc-web-javascript/0.1' -H 'Origin: https://developers.google.com' -H 'DNT: 1' -H 'Sec-GPC: 1' -H 'Connection: keep-alive' -H 'Referer: https://developers.google.com/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-site' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'TE: trailers' -s --data-raw '["{user_id}"]' '''
            )
        else:
            status, output = subprocess.getstatusoutput(
                f'''curl 'https://developerprofiles-pa.clients6.google.com/$rpc/google.internal.developerprofiles.v1.profile.ProfileService/GetPublicProfile'  --compressed -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'X-Goog-Api-Key: {curl_args}' -H 'X-Goog-AuthUser: 0' -H 'Authorization: ' -H 'Content-Type: application/json+protobuf' -H 'X-User-Agent: grpc-web-javascript/0.1' -H 'Origin: https://developers.google.com' -H 'DNT: 1' -H 'Sec-GPC: 1' -H 'Connection: keep-alive' -H 'Referer: https://developers.google.com/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-site' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -s --data-raw '[null,null,"{user_id}"]' '''
            )  # curl because libs don't work
        user_id = json.loads(
            output
        )
        user_id = user_id[-1][-1]
        return user_id
    except httpx.ConnectError:
        if rec_limit == 0:
            print('ConnectError')
            return ""
        time.sleep(0.1)
    return ""

def get_id_by_name(user_id: str, curl_args):
    if type(user_id) != str or user_id.isdigit():
        return user_id
    status, output = subprocess.getstatusoutput(
        f'''curl 'https://developerprofiles-pa.clients6.google.com/$rpc/google.internal.developerprofiles.v1.profile.ProfileService/GetPublicProfile'  --compressed -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'X-Goog-Api-Key: {curl_args}' -H 'X-Goog-AuthUser: 0' -H 'Authorization: ' -H 'Content-Type: application/json+protobuf' -H 'X-User-Agent: grpc-web-javascript/0.1' -H 'Origin: https://developers.google.com' -H 'DNT: 1' -H 'Sec-GPC: 1' -H 'Connection: keep-alive' -H 'Referer: https://developers.google.com/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-site' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -s --data-raw '[null,null,"{user_id}"]' '''
    )  # curl because libs don't work
    user_id = json.loads(
        output
    )
    print(user_id)
    user_id = user_id[1][31]
    return user_id

def get_awards_by_id(user_id: str | int, key: str, curl_args, timeout, rec_limit=10) -> dict:
    print(f'Processing id {user_id}')
    try:
        if not (type(user_id) != str or user_id.isdigit()):
            user_id = get_id_by_name(user_id, curl_args)

        c = httpx.get(f'https://developerprofiles-pa.clients6.google.com/v1/awards?access_token&locale&obfuscatedProfileId={user_id}&useBadges=true&key={key}',
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'X-JavaScript-User-Agent': 'google-api-javascript-client/1.1.0',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Goog-Encode-Response-If-Executable': 'base64',
                'X-ClientDetails': '''appVersion=5.0%20(X11)&platform=Linux%20x86_64&userAgent=Mozilla%2F5.0%20(X11%3B%20Linux%20x86_64%3B%20rv%3A128.0)%20Gecko%2F20100101%20Firefox%2F128.0''',
                'Origin': 'https://developers.google.com',
                'DNT': '1',
                'Sec-GPC': '1',
                'Connection': 'keep-alive',
                'Referer': 'https://developers.google.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'TE': 'trailers',
            },
            timeout=timeout
        ).text
        # print(
        #     c
        # )
        data = json.loads(c)
        award_titles = {
            award.get('badge', {}).get('title', None): award.get('createTime', {})
            for award in data.get('awards', {}) # this line handles bad ids (if err -> no rewards -> 0 on public profile column)
        }
        return award_titles
    except httpx.ConnectError:
        if rec_limit == 0:
            print('ConnectError')
            return {}
        time.sleep(0.1)
        return get_awards_by_id(user_id, key, curl_args, timeout, rec_limit-1)


def get_awards(ids: [str | int], key: str, curl_args, timeout, rec_limit=10) -> dict[set]:
    awards = {}
    for user_id in ids:
        try:
            user_awards = get_awards_by_id(user_id, key, curl_args, timeout, rec_limit)
            awards[user_id] = user_awards
        except Exception as e:
            print(f'Error during processing id = {user_id}, it will be skipped')
            print(e)
    return awards


def write_to_local_csv(awards: dict[set], curl_args, fname: str = 'result.csv', rec_limit=10) -> None:
    column_names = set()
    default_columns = [
        'id',
        'name',
        'url_id',
        'public_profile',
        'profile created',
    ]

    for user_awards in awards.values():
        column_names.update(user_awards)
    column_names = default_columns + sorted(list(column_names))
    with open(fname, 'w', newline='') as csvfile:
        award_writer = csv.writer(csvfile)
        award_writer.writerow(
            column_names
        )
        rows = []
        for user_awards in awards.items():
            row = [
                get_id_by_name(user_awards[0], curl_args),
                get_name(user_awards[0], curl_args, rec_limit),
                user_awards[0],
                1 if len(user_awards[1]) else 0,
                user_awards[1].get('Joined the Google Developer Program'),
            ]
            for award_name in column_names[len(default_columns):]:
                row.append(user_awards[1][award_name] if award_name in user_awards[1] else 'No')
            rows.append(tuple(row))
        for row in set(rows):
            award_writer.writerow(
                row
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='developers.google.com badges exporter',
    )
    parser.add_argument('-o', '--output', default='result.csv')
    parser.add_argument('-i', '--ids_file')
    parser.add_argument('-k', '--key')
    parser.add_argument('-c', '--curl_args')
    parser.add_argument('-t', '--timeout', type=float, default=1)
    parser.add_argument('-r', '--repeat', type=int, default=10)

    parser.add_argument('--google_token', type=str, required=False, help='Specify path to google token file')
    parser.add_argument('--table_id', type=str, required=False)
    parser.add_argument('--sheet_id', type=str, required=False)
    parser.add_argument('--input_sheet_id', type=str, required=False)
    parser.add_argument('--input_column_number', type=int, required=False)
    parser.add_argument('--input_column_skip', type=int, required=False, default=0)

    parser.add_argument('--yandex_token', type=str, required=False)
    parser.add_argument('--yandex_path', type=str, required=False)

    args = parser.parse_args()
    lines = None
    if args.ids_file:
        with open(args.ids_file) as file:
            lines = [line.rstrip() for line in file]
    # ids = lines
    elif args.google_token and args.table_id and args.input_sheet_id:
        print('getting ids from google table')
        lines = sheets.read_ids_from_table(
            args.google_token,
            args.table_id,
            args.input_sheet_id,
            args.input_column_number
        )
        lines = sheets.cut_lines(lines, args.input_column_skip)
    else:
        print('set ids file or google table input')

    print('recieved following ids')
    print(lines)
    q = get_awards(lines, args.key, args.curl_args, args.timeout, args.repeat)
    write_to_local_csv(q, args.curl_args, args.output, args.repeat)
    if args.google_token and args.table_id and args.sheet_id:
        sheets.write_data_to_table(
            pandas.read_csv(args.output),
            args.google_token,
            args.table_id,
            args.sheet_id
        )

    if args.yandex_token and args.yandex_path:
        import yandex_disk
        yandex_disk.DiskManager(
            yatoken=args.yandex_token
        ).upload(
            args.output,
            args.yandex_path
        )
