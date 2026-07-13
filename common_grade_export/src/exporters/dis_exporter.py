# /bin/python3
import logging
import logging.config

import requests
from exporters.base_exporter import BaseExporter
from utils.arg_parser import arg_parser_dis

logging.config.fileConfig('./logging.conf')
logger = logging.getLogger("dis_exporter")

EXPORT_URL = "https://slides-checker.moevm.pro/get_csv/?limit=0&offset=0&sort=&order="


class DISExporter(BaseExporter):
    def download_data(self) -> str:
        url = f"{EXPORT_URL}&{self.args.checker_filter}&access_token={self.args.checker_token}"
        return requests.get(url).content.decode("utf-8")


if __name__ == "__main__":
    args = arg_parser_dis()
    DISExporter(args=args, logger=logger).run()
