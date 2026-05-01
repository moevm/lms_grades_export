# /bin/python3
import logging
import logging.config

import requests
from exporters.base_exporter import BaseExporter
from utils.arg_parser import arg_parser_wst

logging.config.fileConfig('./logging.conf')
logger = logging.getLogger("dis_exporter")

EXPORT_URL = "http://speech-trainer.moevm.info/api/trainings/csv?count=1000&"


class WSTExporter(BaseExporter):
    def download_data(self) -> str:
        url = rf"{EXPORT_URL}&{self.args.wst_filter}&TOKEN={self.args.wst_token}"
        return requests.get(url).content.decode("utf-8")


if __name__ == "__main__":
    args = arg_parser_wst()
    WSTExporter(args=args, logger=logger).run()
