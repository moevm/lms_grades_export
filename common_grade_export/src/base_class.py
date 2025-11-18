import logging
import sys
from io import StringIO
from utils.download_file import download_sheet, get_sheets_service_and_token

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class BaseGoogleSpreadsheetDataProcessor:
    def __init__(
        self,
        table_id: str,
        sheet_id: str,
        google_cred: str,
    ):
        """
        Инициализация базовых полей

        Args:
            table_id (str): ID управляющей таблицы
            sheet_id (str): ID листа в управляющей таблицы
            google_cred (str): Путь к файлу учетных данных Google
        """
        self.table_id = table_id
        self.sheet_id = sheet_id
        self.google_cred = google_cred
        self.results = []
        self.has_errors = False

    def validate_google_credentials(self):
        # TODO: validate creds and wite access to table
        pass

    def get_control_data(self) -> StringIO | None:
        """
        Получает данные из управляющей таблицы
        """
        content = download_sheet(
            table_id=self.table_id,
            sheet_id=self.sheet_id,
            google_cred=self.google_cred,
            export_format="csv",
            write_to_file=False,
        )

        if content:
            return StringIO(content.decode("utf-8"))
        else:
            return None

    def set_errors_flag(self, flag=True):
        self.has_errors = flag

    def check_errors(self):
        return not self.has_errors

    def process(self):
        """
        Обрабатывает данные экспорта
        """
        raise NotImplementedError()

    def process_data(self, table_id: str, sheet_id: str, *args, **kwargs) -> str:
        """
        Обрабатывает одну строку данных

        Args: данные строки из таблицы
        """
        raise NotImplementedError()

    def write_process_result(
        self, table_range="A1", rows=100, cols=2, prefix="result_"
    ):
        """
        Записывает результаты обработки в управляющую таблицу в table_range (по умолчанию A1), очищая старые данные.
        rows, cols используются для создания нового листа, в случае его отсутствия

        Используется self.results - должен иметь формат list[list[str]] (список вставляемых строк), например:
        [
            [header1, header2, ...],
            [row1_col1, row1_col2, ...],
            [row2_col1, row2_col2, ...],
        ]
        """
        client, _ = get_sheets_service_and_token(self.google_cred)
        sh = client.open_by_key(self.table_id)

        sheet_title = f"{prefix}{sh.get_worksheet_by_id(self.sheet_id).title}"

        try:
            ws = sh.worksheet(sheet_title)
            ws.clear()
        except:
            ws = sh.add_worksheet(title=sheet_title, rows=rows, cols=cols)

        ws.append_rows(self.results, table_range=table_range)
