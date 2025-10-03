import argparse
import gspread
from io import BytesIO
import logging
from openpyxl import Workbook
import requests
from pathlib import Path
from google.oauth2 import service_account
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


# TODO: class for google service


def get_sheets_service_and_token(credentials_file="credentials.json"):
    """Создает и возвращает сервис для работы с Google Sheets и API access_token"""
    creds = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ],
    )
    client = gspread.authorize(creds)
    creds.refresh(Request())
    return client, creds.token


def download_sheet(
    table_id,
    sheet_id="0",
    filename="export",
    export_format="pdf",
    google_cred="credentials.json",
    write_to_file=True,
) -> bytes | None:
    try:
        client, access_token = get_sheets_service_and_token(google_cred)
        if export_format == "xlsx":
            content = get_excel_with_values(client, table_id, sheet_id)
        else:
            content = export_file(table_id, sheet_id, access_token, export_format)

        if not content:
            logger.error(f"Ошибка экспорта файла")
            return None

        if write_to_file:
            new_filepath = Path(f"{filename}.{export_format}")
            new_filepath.parents[0].mkdir(parents=True, exist_ok=True)
            with open(new_filepath, "wb") as f:
                f.write(content)
            logger.debug(f"Файл сохранен как: {new_filepath}")
        return content

    except Exception as e:
        logger.error(f"Ошибка при скачивании: {e}")


def get_excel_with_values(
    service: gspread.Client, table_id: str, sheet_id: str
) -> bytes:
    """
    Сохраняет значения (не формулы) листа таблицы в XLSX-файл
    """
    spreadsheet = service.open_by_key(table_id)
    worksheet = spreadsheet.get_worksheet_by_id(int(sheet_id))
    data = worksheet.get_all_values()

    wb = Workbook()
    ws = wb.active
    ws.title = worksheet.title

    for row in data:
        ws.append(row)

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return file_stream.read()


def export_file(
    table_id: str, sheet_id: str, access_token: str, export_format: str
) -> bytes | None:
    """
    Экспортирует файл используя export-url
    """
    url = f"https://docs.google.com/spreadsheets/d/{table_id}/export?format={export_format}&gid={sheet_id}"

    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})

    if response.status_code == 200:
        return response.content
    else:
        logger.error(f"export_file: Ошибка {response.status_code}: {response.text}")
        return None


def parse_args():
    parser = argparse.ArgumentParser(description="Download Google Sheets")
    parser.add_argument("--table_id", required=True, help="Google Sheets table ID")
    parser.add_argument(
        "--sheet_id", required=True, default="0", type=str, help="Sheet ID (default: 0)"
    )
    parser.add_argument(
        "--format", choices=["csv", "pdf", "xlsx"], default="csv", help="Output format"
    )
    parser.add_argument(
        "--filename", default="export", help="Output filename (without extension)"
    )
    parser.add_argument("--google_cred", help="Path to google credentials file")

    return parser.parse_args()


def main():
    args = parse_args()

    download_sheet(
        args.table_id, args.sheet_id, args.filename, args.format, args.google_cred
    )


if __name__ == "__main__":
    main()
