import argparse
import csv
import subprocess
import sys
from json import load as json_load
import logging
from pathlib import Path
from base_class import BaseGoogleSpreadsheetDataProcessor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class CourseToSpreadheetExporter(BaseGoogleSpreadsheetDataProcessor):

    def __init__(
        self, table_id: str, sheet_id: str, google_cred: str, system_cred_path: str
    ):
        super().__init__(table_id, sheet_id, google_cred)
        self.systems = {"moodle", "dis", "stepik"}
        self.system_cred = self.validate_system_credentials(
            self.load_system_creds(system_cred_path)
        )
        self.results = [["subject", "table_link"]]

    @staticmethod
    def load_system_creds(path: str) -> dict:
        with open(path, encoding="utf-8") as file:
            return json_load(file)

    def validate_system_credentials(self, system_cred: dict) -> dict:
        # TODO: real validation?
        if not all(system_cred.values()):
            # Значения всех систем = None -> не можем ничего выгружать
            raise ValueError(
                f"Нет каких-либо валидных данных для систем: {system_cred}"
            )
        valid_systems = self.systems and set(system_cred.keys())
        if not valid_systems:
            # Нет валидных систем -> не можем ничего выгружать
            raise ValueError(f"Нет валидных систем в данных: {system_cred.keys()}")
        return {key: system_cred[key] for key in valid_systems}

    def process(self) -> bool:
        control_data = self.get_control_data()

        if control_data:
            control_data = csv.DictReader(
                control_data,
                fieldnames=[
                    "subject",
                    "table_id",
                    "sheet_id",
                    "system",
                    "main_export_info",
                    "additional_export_info",
                ],
            )
            for export_line in control_data:
                subject = export_line.pop("subject")
                try:
                    logger.info(f">>>>> Экспорт для дисциплины {subject}")
                    is_ok = self.process_data(**export_line)
                    self.results.append(
                        [
                            subject,
                            f"https://docs.google.com/spreadsheets/d/{export_line['table_id']}/edit?gid={export_line['sheet_id']}",
                        ]
                        if is_ok
                        else [subject, "- (error)"]
                    )
                except Exception as e:
                    logger.info(f"!!!!! Ошибка при экспорте дисциплины {subject}: {e}")
                    self.results.append([subject, "- (error)"])
                    self.set_errors_flag()
                finally:
                    logger.info(f">>>>> Конец экспорта для дисциплины {subject}")

            self.write_process_result()
            return self.check_errors()
        else:
            logger.error("Ошибка получения данных для экспорта")
            return False

    def process_data(self, system, **export_info) -> bool:
        """
        Обрабатывает одну строку данных - одиночная выгрузка

        Args: данные строки из таблицы
        """

        if system not in self.system_cred:
            raise ValueError(
                f"Для системы {system} нет валидных данных в {self.system_cred}"
            )
        return self.run_export(system, **export_info)

    def run_export(self, system: str, **export_info) -> bool:
        """
        Запускает docker-контейнер с выгрузкой данных

        Return:
            bool: docker run command returncode == 0
        """
        docker_run_cmd = self.create_docker_run_cmd(system, **export_info)
        result = subprocess.run(docker_run_cmd, capture_output=True, text=True)
        if result.stdout:
            logger.info(f"docker stdout: '''{result.stdout}'''")
        if result.stderr:
            logger.error(f"docker stderr: '''{result.stderr}'''")
        return result.returncode == 0

    def create_docker_run_cmd(
        self, system: str, table_id: str, sheet_id: str, **export_info
    ) -> list[str]:
        """
        Формирует полную команду запуска docker run
        """
        cmd = ["docker", "run", "--rm", "-v", f"{self.google_cred}:/app/conf.json"]
        cmd.extend(["--name", f"{system}_exporter"])
        cmd.extend(self.get_extended_system_docker_command(system, **export_info))
        cmd.extend(
            [
                "--table_id",
                table_id,
                "--sheet_id",
                sheet_id,
                "--google_token",
                "conf.json",
            ]
        )
        return cmd

    def get_extended_system_docker_command(
        self,
        system: str,
        main_export_info: str,
        additional_export_info: str | None = None,
    ) -> list[str]:
        """
        Формирует системо-зависимую часть команды docker run для выгрузки
        """
        CMD = {
            "moodle": [
                "moodle_export_parser:latest",
                "--moodle_token",
                self.system_cred["moodle"],
                "--url",
                "https://e.moevm.info",
                "--csv_path",
                "grades",
                "--course_id",
                main_export_info,
                "--options",
                "github",
            ],
            "stepik": [
                "stepik_export_parser:latest",
                "--client_id",
                self.system_cred["stepik"]["client_id"],
                "--client_secret",
                self.system_cred["stepik"]["client_secret"],
                "--url",
                "https://stepik.org:443/api",
                "--csv_path",
                "grades",
                "--course_id",
                main_export_info,
                "--class_id",
                additional_export_info,
            ],
            "dis": [
                "checker_export_parser:latest",
                "--checker_filter",
                main_export_info,
                "--checker_token",
                self.system_cred["dis"],
            ],
        }
        return CMD[system]


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
        "--system_cred",
        required=True,
        help="Path to system (moodle/stepik/dis) credentials file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    exporter = CourseToSpreadheetExporter(
        table_id=args.table_id,
        sheet_id=args.sheet_id,
        google_cred=args.google_cred,
        system_cred_path=args.system_cred,
    )

    if not exporter.process():
        exit(1)
