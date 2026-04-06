# /bin/python3
import csv
from io import StringIO

import pandas as pd
import requests

from utils.download_file import get_sheets_service_and_token
from utils.arg_parser import arg_parser_wst



EXPORT_URL = "http://speech-trainer.moevm.info/api/trainings/csv?count=1000&"


def load_data_from_wst(wst_filter, wst_token):
    url = fr"{EXPORT_URL}&{wst_filter}&TOKEN={wst_token}"
    print(url, requests.get(url))
    print(requests.get(url).content)
    csv_data = StringIO(requests.get(url).content.decode("utf-8"))

    df = pd.read_csv(csv_data)
    df_data = pd.DataFrame(df.to_dict("records"))

    return csv_data, df_data


def write_data_to_table(
    wst_token,
    wst_filter,
    google_token,
    table_id,
    sheet_id,
    start_cell="A1"
):
    csv_data, _ = load_data_from_wst(wst_filter, wst_token)

    if google_token and sheet_id and table_id:
        gc, _ = get_sheets_service_and_token(google_token)
        sh = gc.open_by_key(table_id)

        wk_content = sh.get_worksheet_by_id(sheet_id)
        print(csv_data)
        reader = csv.reader(csv_data)
        b = []
        for a in reader:
            print(a)
            b.append(a)
        print(a)
        wk_content.update(values=b, range_name=start_cell)
        print(f"WST data's writed to {table_id} {sheet_id}")


def main():
    args = arg_parser_wst()
    write_data_to_table(
        wst_token=args.wst_token,
        wst_filter=args.wst_filter,
        google_token=args.google_token,
        table_id=args.table_id,
        sheet_id=args.sheet_id,
        start_cell=args.start_cell
    )


if __name__ == "__main__":
    main()
