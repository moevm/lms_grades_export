import argparse
import datetime
import logging
import os
import re
import typing
from urllib.parse import urlencode

import filetype
import requests
import yadisk
from bs4 import BeautifulSoup

GOOGLE_DRIVE_URL = 'https://drive.google.com'
GOOGLE_DOCS_URL = 'https://docs.google.com'
CLOUD_MAIL_URL = 'https://cloud.mail.ru'
YANDEX_DISK_URL = 'https://disk.yandex.ru'

FILES_TO_IGNORE = ("main.py", "README.md", "requirements.txt")

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

download_logger = logging.getLogger('download_logger')
download_logger.setLevel(logging.INFO)

report_logger = logging.getLogger('report_logger')
report_logger.setLevel(logging.INFO)
current_time = datetime.datetime.now().strftime("%y_%m_%d_%H:%M")
fh = logging.FileHandler(f"{current_time}_download_report.log", mode='w')
report_logger.addHandler(fh)

link_count = 0
successful_download_count = 0
failed_download_count = 0
overwritten_files_count = 0
empty_url_count = 0
failed_filetype_determination_count = 0
current_prefix = None


def get_data_from_google_spreadsheet(url) -> typing.List[typing.List[str]]:
    if 'edit' in url:
        # This is needed to change the format google returns the spreadsheet in
        # which helps avoid working with empty cells and allows processing bigger spreadsheets
        temp = url.split('/')
        temp[-1] = 'gviz/tq?tqx=out:html&tq&gid=1'
        url = '/'.join(temp)

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    salas_cine = soup.find_all('table')[0]
    rows = [[td.text for td in row.find_all("td")] for row in salas_cine.find_all('tr')]
    return rows


def get_file_content_from_cloud_mail_ru(url):
    global failed_download_count
    old_url = url
    # link should look like 'https://cloud.mail.ru/public/XXX/YYYYYYYY'
    response = requests.get(url)
    if response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        report_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        failed_download_count = failed_download_count + 1
        return None
    page_content = response.text

    re_pattern = r'dispatcher.*?weblink_get.*?url":"(.*?)"'
    match = re.search(re_pattern, page_content)

    if match:
        url = match.group(1)
        # get /XXX/YYYYYYYY from source link
        parts = old_url.split('/')[-2:]
        # add XXX and YYYYYYYY to result link
        url = f'{url}/{parts[0]}/{parts[1]}'
        file_response = requests.get(url)
        if file_response.status_code != 200:
            download_logger.error(f"{current_prefix}: couldn't get file download link for {old_url}")
            report_logger.error(f"{current_prefix}: couldn't get file download link for {old_url}")
            failed_download_count = failed_download_count + 1
            return None

        download_logger.info(f"Successfully accessed file at {old_url}")
        return file_response

    download_logger.error(f"{current_prefix}: couldn't get file download link for {old_url}")
    report_logger.error(f"{current_prefix}: couldn't get file download link for {old_url}")
    failed_download_count = failed_download_count + 1
    return None


def get_file_content_from_google_drive(url):
    global failed_download_count
    temp_url = "https://docs.google.com/uc?export=download&confirm=1"

    response = requests.get(url)
    if response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        report_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        failed_download_count = failed_download_count + 1
        return None

    file_id = url.split('/')[-2]
    session = requests.Session()
    file_response = session.get(temp_url, params={"id": file_id})
    if file_response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't get file download link for {url}")
        report_logger.error(f"{current_prefix}: couldn't get file download link for {url}")
        failed_download_count = failed_download_count + 1
        return None

    download_logger.info(f"Successfully accessed file at {url}")
    return file_response


def get_file_content_from_google_docs(url):
    global failed_download_count

    response = requests.get(url)
    if response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        report_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        failed_download_count = failed_download_count + 1
        return None

    file_id = url.split('/')[-2]
    final_url = f'https://docs.google.com/document/u/0/export?format=pdf&id={file_id}'

    final_response = requests.get(final_url)
    if final_response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't get file download link for {url}")
        report_logger.error(f"{current_prefix}: couldn't get file download link for {url}")
        failed_download_count = failed_download_count + 1
        return None

    download_logger.info(f"Successfully accessed file at {url}")
    return final_response


def get_file_content_from_yandex_disk(url):
    global failed_download_count
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

    response = requests.get(url)
    if response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        report_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        failed_download_count = failed_download_count + 1
        return None

    final_url = base_url + urlencode(dict(public_key=url))
    response = requests.get(final_url)
    if response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        report_logger.error(f"{current_prefix}: couldn't access/file deleted {url}")
        failed_download_count = failed_download_count + 1
        return None

    download_url = response.json()['href']
    file_response = requests.get(download_url)

    if file_response.status_code != 200:
        download_logger.error(f"{current_prefix}: couldn't get file download link for {url}")
        report_logger.error(f"{current_prefix}: couldn't get file download link for {url}")
        failed_download_count = failed_download_count + 1
        return None

    download_logger.info(f"Successfully accessed file at {url}")
    return file_response


def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def process_url(url):
    global failed_download_count
    download_logger.info(f"Processing {url}")
    if GOOGLE_DRIVE_URL in url:
        download_logger.info(f"{url} parsed as a Google drive url")
        return get_file_content_from_google_drive(url)
    if GOOGLE_DOCS_URL in url:
        download_logger.info(f"{url} parsed as a Google docs url")
        return get_file_content_from_google_docs(url)
    if CLOUD_MAIL_URL in url:
        download_logger.info(f"{url} parsed as a Cloud mail.ru url")
        return get_file_content_from_cloud_mail_ru(url)
    if YANDEX_DISK_URL in url:
        download_logger.info(f"{url} parsed as a Yandex disk url")
        return get_file_content_from_yandex_disk(url)
    download_logger.error(f"{url} couldn't be parsed as any known file storage service url")
    failed_download_count = failed_download_count + 1
    return None


def download_files(rows, prefix_column_index, download_column_index, download_column_name):
    global \
        empty_url_count, \
        successful_download_count, \
        link_count, \
        failed_filetype_determination_count, \
        current_prefix, \
        overwritten_files_count
    rows.pop(0)
    download_logger.info("Starting to download files from urls")
    for row in rows:
        prefix = row[prefix_column_index]
        current_prefix = prefix
        download_url = row[download_column_index]
        if download_url == '\xa0':
            download_logger.error(f"{prefix}'s download url is empty")
            report_logger.error(f"{prefix}'s download url is empty")
            empty_url_count = empty_url_count + 1
            continue

        link_count = link_count + 1
        download_logger.info(f"Processing {prefix} {download_url}")
        download_file_response = process_url(download_url)

        if download_file_response:
            download_file_name = f'{prefix}_{download_column_name}'
            try:
                download_file_type = filetype.guess(download_file_response.content).EXTENSION
                download_file_name = download_file_name + '.' + download_file_type
            except AttributeError:
                failed_filetype_determination_count = failed_filetype_determination_count + 1
                download_logger.error(f"Couldn't determine filetype for {download_file_name}")
                report_logger.error(f"Couldn't determine filetype for {download_file_name}")

            if os.path.isfile(download_file_name):
                download_logger.info(f"{download_file_name} already exists, it will be overwritten")
                report_logger.info(f"{download_file_name} already exists, it will be overwritten")
                overwritten_files_count = overwritten_files_count + 1
            else:
                download_logger.info(f"Writing downloaded file {download_file_name} to disk")
                report_logger.info(f"File {download_file_name} downloaded successfully from {download_url}")

            successful_download_count = successful_download_count + 1
            save_response_content(download_file_response, download_file_name)


def main():
    parser = argparse.ArgumentParser(
        description="A script for downloading files from links in a column in Google spreadsheet"
    )
    parser.add_argument('--table_link', required=True)
    parser.add_argument('--credentials', required=True)
    parser.add_argument('--prefix_column_name', required=True)
    parser.add_argument('--download_column_name', required=True)
    parser.add_argument('--cloud_directory_path', required=True)
    args = parser.parse_args()

    logger.info(f"Accessing spreadsheet {args.table_link}")
    rows = get_data_from_google_spreadsheet(args.table_link)
    column_names = rows[0]
    prefix_column_index = None
    download_column_index = None
    for i in range(len(column_names)):
        if column_names[i] == args.prefix_column_name:
            prefix_column_index = i
            logger.info(f"Found prefix column {args.prefix_column_name}'s index: {prefix_column_index}")
            break

    for i in range(len(column_names)):
        if column_names[i] == args.download_column_name:
            download_column_index = i
            logger.info(f"Found download column {args.download_column_name}'s index: {download_column_index}")
            break

    if not prefix_column_index:
        logger.error(f"No prefix column with provided name ({args.prefix_column_name}) found")
        report_logger.error(f"No prefix column with provided name ({args.prefix_column_name}) found")
        return

    if not download_column_index:
        logger.error(f"No download column with provided name ({args.download_column_name}) found")
        report_logger.error(f"No download column with provided name ({args.prefix_column_name}) found")
        return

    report_logger.info(f"prefix_column_name: {args.prefix_column_name}")
    report_logger.info(f"download_column_name: {args.download_column_name}")
    report_logger.info("---------------------------------------------------------")

    download_files(rows, prefix_column_index, download_column_index, args.download_column_name)

    report_logger.info("---------------------------------------------------------")
    report_logger.info(f"Total links: {link_count}")
    report_logger.info(f"Successful downloads: {successful_download_count}")
    report_logger.info(f"Failed downloads: {failed_download_count}")
    report_logger.info(f"Overwritten files: {overwritten_files_count}")
    report_logger.info(f"Empty cells in download column: {empty_url_count}")
    report_logger.info(f"Failed filetype determinations: {failed_filetype_determination_count}")
    report_logger.info("---------------------------------------------------------")

    client = yadisk.Client(token=args.credentials)
    successful_upload_count = 0
    cloud_directory_path = args.cloud_directory_path

    if cloud_directory_path[-1] != '/':
        cloud_directory_path = cloud_directory_path + '/'

    try:
        if client.check_token():
            if not client.is_dir(cloud_directory_path):
                client.mkdir(cloud_directory_path)
                report_logger.info(f"Directory {cloud_directory_path} created")
    except Exception:
        report_logger.error(f"Directory {cloud_directory_path} creation failed")
        cloud_directory_path = ''
        report_logger.error("Files will be uploaded to cloud disk root")

    for filename in os.listdir():
        if ".log" in filename:
            continue
        if filename in FILES_TO_IGNORE:
            continue
        try:
            cloud_filepath = cloud_directory_path + filename
            client.upload(filename, cloud_filepath, overwrite=True, n_retries=10)
            report_logger.info(f"{cloud_filepath} uploaded successfully ")
            successful_upload_count = successful_upload_count + 1
        except Exception:
            report_logger.info(f"{filename} upload failed")

    report_logger.info("---------------------------------------------------------")
    report_logger.info(f"Successful file downloads from google spreadsheet: {successful_download_count}")
    report_logger.info(f"Overwritten files: {overwritten_files_count}")
    report_logger.info(f"Successful file uploads to Yandex Disk: {successful_upload_count}")


if __name__ == '__main__':
    main()
