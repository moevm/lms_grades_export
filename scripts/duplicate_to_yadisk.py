#!/usr/bin/env python3
"""
Модуль для экспорта таблиц и загрузки на Яндекс.Диск
Заменитель bash-скрипта duplicate_to_yadisk.sh
"""

import argparse
import csv

# import sys
import logging
from download_file import download_sheet, get_sheets_service_and_token
from yadisk_manager import DiskManager


# logging.basicConfig(
#    level=logging.INFO,
#    format="%(asctime)s - %(levelname)s - %(message)s",
#    handlers=[
#        logging.FileHandler("duplicate_sheets.log", mode="w", encoding="utf-8"),
#        logging.StreamHandler(sys.stdout),
#    ],
# )
logger = logging.getLogger(__name__)


class Exporter:
    def __init__(
        self,
        table_id: str,
        sheet_id: int,
        google_cred: str,
        yadisk_token: str,
        yadisk_dir: str,
    ):
        """
        Инициализация экспортера

        Args:
            table_id (str): ID управляющей таблицы
            sheet_id (str): ID листа в управляющей таблицы
            google_cred (str): Путь к файлу учетных данных Google
            yadisk_token (str): OAuth-токен Яндекс.Диска
            yadisk_dir (str): Целевая директория на Яндекс.Диске
        """
        self.table_id = table_id
        self.sheet_id = sheet_id
        self.google_cred = google_cred
        self.yadisk_dir = yadisk_dir
        self.disk_manager = DiskManager(token=yadisk_token)
        self.results = [["filename", "public_link"]]
        self.has_errors = False

    def process(self):
        """
        Обрабатывает данные экспорта
        """
        export_content = download_sheet(
            table_id=self.table_id,
            sheet_id=self.sheet_id,
            google_cred=self.google_cred,
            export_format="csv",
            write_to_file=False,
        )
        if export_content:
            export_data = csv.DictReader(
                export_content,
                fieldnames=[
                    "subject",
                    "table_id",
                    "sheet_id",
                    "export_format",
                    "export_name",
                ],
            )
            for export_line in export_data:
                subject = export_line.pop("subject")
                try:
                    logger.info(f">>>>> Экспорт для дисциплины {subject}")
                    link = self.process_export(**export_line)
                    self.results.append([export_line["export_name"], link])
                except Exception as e:
                    logger.error(f"!!!!! Ошибка при экспорте дисциплины {subject}: {e}")
                    self.results.append([export_line["export_name"], "- (error)"])
                    self.has_errors = True
                finally:
                    logger.info(f">>>>> Конец экспорта для дисциплины {subject}")

            self.write_export_result()
            return not self.has_errors
        else:
            logger.error("Ошибка получения данных для экспорта")
            return False

    def process_export(
        self,
        table_id: str,
        sheet_id: str,
        export_name: str,
        export_format: str,
    ) -> str:
        """
        Экспортирует один лист дисциплины

        Args: данные строки из таблицы
        """
        if sheet_id.isdecimal():
            int_sheet_id = int(sheet_id)
        else:
            raise Exception(f"process_export: sheet_id={sheet_id} is'not int")

        export_success = download_sheet(
            table_id=table_id,
            sheet_id=int_sheet_id,
            export_format=export_format,
            filename=export_name,
            google_cred=self.google_cred,
        )

        if not export_success:
            raise Exception(f"process_export: download_sheet error")

        public_link = self.upload_file_to_disk(f"{export_name}.{export_format}")
        if not public_link:
            raise Exception(f"process_export: upload_file_to_disk error")
        return public_link

    def upload_file_to_disk(self, file_path: str):
        """Загрузка файла на диск и его публикация

        Args:
            file_path (str): path to local file
        Return:
            str: public link to file
        """
        full_path = f"{self.yadisk_dir}/{file_path}"
        self.disk_manager.upload(file_path, full_path)
        return self.disk_manager.publish_file(full_path)

    def write_export_result(self):
        client, _ = get_sheets_service_and_token(self.google_cred)
        sh = client.open_by_key(self.table_id)

        sheet_title = f"result_{sh.get_worksheet_by_id(self.sheet_id).title}"

        try:
            ws = sh.worksheet(sheet_title)
            ws.clear()
        except:
            ws = sh.add_worksheet(title=sheet_title, rows=100, cols=2)

        ws.append_rows(self.results)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download Admin Google Sheets with duplicate info"
    )
    parser.add_argument("--table_id", required=True, help="Google Sheets table ID")
    parser.add_argument(
        "--sheet_id", required=True, default=0, type=int, help="Sheet ID (default: 0)"
    )
    parser.add_argument(
        "--google_cred", required=True, help="Path to google credentials file"
    )
    parser.add_argument(
        "--yadisk_token", required=True, help="Yadisk token for upload/publish"
    )
    parser.add_argument(
        "--yadisk_dir",
        required=True,
        help="Abs path to main Yadisk dir for upload/publish",
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    exporter = Exporter(
        table_id=args.table_id,
        sheet_id=args.sheet_id,
        google_cred=args.google_cred,
        yadisk_token=args.yadisk_token,
        yadisk_dir=args.yadisk_dir,
    )

    if not exporter.process():
        exit(1)
