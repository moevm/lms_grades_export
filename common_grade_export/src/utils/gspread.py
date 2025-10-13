import csv
import os
from io import StringIO

import pandas as pd
import pygsheets

CSV_DELIMITER = os.getenv("CSV_DELIMITER", ";")


def add_csv_to_table(
    csv_filepath, workbook, sheet_name="export", delimiter=CSV_DELIMITER
):
    # delete existing sheet to rewrite
    if sheet_name in workbook.sheetnames:
        # workbook.remove(workbook[sheet_name])
        ws = workbook[sheet_name]
        ws.insert_rows(
            idx=0, amount=0
        )  # clear sheet instead removing, that can break formulas
    else:
        ws = workbook.create_sheet(sheet_name)

    with open(csv_filepath, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            ws.append(row)


def write_data_to_table(
    df_data, google_token, table_id, sheet_name=None, sheet_id=None
):
    if google_token and (sheet_name or sheet_id) and table_id:
        gc = pygsheets.authorize(service_file=google_token)
        sh = gc.open_by_key(table_id)

    if sheet_id:
        wk_content = sh.worksheet("id", sheet_id)
    else:
        try:
            sh.worksheets("title", sheet_name)
        except:
            sh.add_worksheet(sheet_name)

        wk_content = sh.worksheet_by_title(sheet_name)

    # wk_content.set_dataframe(df_data, "A1", copy_head=True) # problem w/float dot
    stream = StringIO(df_data.to_csv(sep=',', encoding='utf-8', decimal=','))
    df = pd.read_csv(stream)
    df_data = pd.DataFrame(df.to_dict("records"))
    wk_content.set_dataframe(df=df_data, start="A1", copy_head=True)


def add_csv_to_table_dis(
    csv_filepath, workbook, sheet_name="export", delimiter=CSV_DELIMITER
):
    # clear sheet instead removing, that can break formulas
    if sheet_name in workbook.sheetnames:
        # workbook.remove(workbook[sheet_name])
        ws = workbook[sheet_name]
        ws.insert_rows(idx=0, amount=0)
    else:
        ws = workbook.create_sheet(sheet_name)

    with open(csv_filepath, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            ws.append(row)


def write_data_to_table_stepik(
    csv_path, google_token, table_id, sheet_name=None, sheet_id=None
):
    if google_token and (sheet_id or sheet_name) and table_id:
        gc = pygsheets.authorize(service_file=google_token)
        sh = gc.open_by_key(table_id)

    if sheet_id:
        wk_content = sh.worksheet("id", sheet_id)
    else:
        try:
            sh.worksheets("title", sheet_name)
        except:
            sh.add_worksheet(sheet_name)

        wk_content = sh.worksheet_by_title(sheet_name)

    if csv_path:
        df = pd.read_csv(csv_path)
        df.fillna(0, inplace=True)
        content = pd.DataFrame(df.to_dict("records"))

    wk_content.set_dataframe(content, "A1", copy_head=True)
