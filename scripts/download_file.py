import argparse
import gspread
import requests
from pathlib import Path
from gspread.utils import ExportFormat
from google.oauth2 import service_account
from google.auth.transport.requests import Request


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
    sheet_id=0,
    filename="export",
    export_format="pdf",
    google_cred="credentials.json",
):
    try:
        _, access_token = get_sheets_service_and_token(google_cred)

        url = f"https://docs.google.com/spreadsheets/d/{table_id}/export?format={export_format}&gid={sheet_id}"

        response = requests.get(
            url, headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code == 200:
            new_filepath = Path(f"{filename}.{export_format}")
            new_filepath.parents[0].mkdir(parents=True, exist_ok=True)
            with open(new_filepath, "wb") as f:
                f.write(response.content)
            print(f"Файл сохранен как: {filename}.{export_format}")
        else:
            print(f"Ошибка {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Ошибка при скачивании: {e}")


def main():
    parser = argparse.ArgumentParser(description="Download Google Sheets")
    parser.add_argument("--table_id", required=True, help="Google Sheets table ID")
    parser.add_argument(
        "--sheet_id", required=True, default=0, type=int, help="Sheet ID (default: 0)"
    )
    parser.add_argument(
        "--format", choices=["csv", "pdf", "xlsx"], default="csv", help="Output format"
    )
    parser.add_argument(
        "--filename", default="export", help="Output filename (without extension)"
    )
    parser.add_argument("--google_cred", help="Path to google credentials file")

    args = parser.parse_args()

    download_sheet(
        args.table_id, args.sheet_id, args.filename, args.format, args.google_cred
    )


if __name__ == "__main__":
    main()
