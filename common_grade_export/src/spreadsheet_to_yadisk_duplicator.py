#!/usr/bin/env python3
"""
Модуль для экспорта таблиц и загрузки на Яндекс.Диск
"""

import argparse
import csv
import logging
import sys
from pathlib import Path

from base_class import BaseGoogleSpreadsheetDataProcessor
from utils.download_file import download_sheet
from utils.yadisk_manager import DiskManager

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class SpreadheetToYaDiskDuplicator(BaseGoogleSpreadsheetDataProcessor):
    def __init__(
        self,
        table_id: str,
        sheet_id: str,
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
        super().__init__(table_id=table_id, sheet_id=sheet_id, google_cred=google_cred)
        self.yadisk_dir = yadisk_dir
        self.disk_manager = DiskManager(token=yadisk_token)
        self.results = [["filename", "public_link"]]

    def process(self):
        """
        Обрабатывает данные экспорта
        """
        control_data = self.get_control_data()

        if control_data:
            control_data = csv.DictReader(
                control_data,
                fieldnames=[
                    "subject",
                    "table_id",
                    "sheet_id",
                    "export_format",
                    "export_name",
                ],
            )
            for export_line in control_data:
                subject = export_line.pop("subject")
                filepath = (
                    f"{export_line['export_name']}.{export_line['export_format']}"
                )
                try:
                    logger.info(f">>>>> Экспорт для дисциплины {subject}")
                    link = self.process_data(**export_line)
                    self.results.append([export_line["export_name"], link])
                except Exception as e:
                    logger.error(f"!!!!! Ошибка при экспорте дисциплины {subject}: {e}")
                    self.results.append([export_line["export_name"], "- (error)"])
                    self.set_errors_flag()
                finally:
                    logger.info(f">>>>> Конец экспорта для дисциплины {subject}")
                    Path(filepath).unlink(missing_ok=True)  # remove from host

            self.write_process_result()
            return self.check_errors()
        else:
            logger.error("Ошибка получения данных для экспорта")
            return False

    def process_data(
        self,
        table_id: str,
        sheet_id: str,
        export_name: str,
        export_format: str,
    ) -> str:
        """
        Обрабатывает одну строку управляющей таблицы

        Args: данные строки из таблицы
        """
        export_success = download_sheet(
            table_id=table_id,
            sheet_id=sheet_id,
            export_format=export_format,
            filename=export_name,
            google_cred=self.google_cred,
        )

        if not export_success:
            raise Exception(f"download_sheet error")

        public_link = self.upload_file_to_disk(f"{export_name}.{export_format}")
        if not public_link:
            raise Exception(f"upload_file_to_disk error")
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

    duplicator = SpreadheetToYaDiskDuplicator(
        table_id=args.table_id,
        sheet_id=args.sheet_id,
        google_cred=args.google_cred,
        yadisk_token=args.yadisk_token,
        yadisk_dir=args.yadisk_dir,
    )

    if not duplicator.process():
        exit(1)
