from abc import ABC, abstractmethod
from argparse import Namespace
from dataclasses import dataclass
from io import StringIO
from logging import Logger

import pygsheets
from pandas import DataFrame, read_csv


@dataclass
class TableConfig:
    token: str
    table_id: str
    sheet_id: int
    start_cell: str = "A1"

    def is_correct(self):
        return self.token and self.sheet_id and self.table_id


class BaseExporter(ABC):
    def __init__(self, args: Namespace, logger: Logger):
        self.args = args
        self.logger = logger
        self.tconfig = TableConfig(
            token=args.google_token,
            table_id=args.table_id,
            sheet_id=args.sheet_id,
            start_cell=args.start_cell,
        )
        if not self.tconfig.is_correct():
            msg = f"Table params aren't set: {self.tconfig}"
            self.logger.info(msg)
            raise Exception(msg)

    @abstractmethod
    def download_data(self) -> str:
        pass

    def run(self):
        self.logger.info(f"Start to {self.tconfig.table_id} {self.tconfig.sheet_id}")
        self.write_data_to_table()
        self.logger.info(f"Finished to {self.tconfig.table_id} {self.tconfig.sheet_id}")

    def write_data_to_table(self):
        raw_data = self.download_data()
        _, df_data = self.save_csv_to_file_and_dataframe(raw_data)
        self.add_dataframe_to_table(df=df_data)

    def add_dataframe_to_table(self, df: DataFrame):
        gc = pygsheets.authorize(service_file=self.tconfig.token)
        sh = gc.open_by_key(self.tconfig.table_id)
        wk_content = sh.worksheet("id", self.tconfig.sheet_id)
        wk_content.set_dataframe(df=df, start=self.tconfig.start_cell, copy_head=True)

    def save_csv_to_file_and_dataframe(self, csv_data: str) -> tuple[str, DataFrame]:
        if csv_data:
            df = read_csv(StringIO(csv_data))
            df_data = DataFrame(df.to_dict("records"))
        else:
            df_data = DataFrame({})
        csv_path = "./results.csv"
        with open(csv_path, mode="w", encoding="utf-8") as file:
            file.write(csv_data)
        return csv_path, df_data
