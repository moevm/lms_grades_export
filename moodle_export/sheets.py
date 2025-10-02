import pygsheets
import pandas as pd
import args_parser


def write_data_to_table(df_data, google_token, table_id, sheet_name=None, sheet_id=None):
    if google_token and (sheet_name or sheet_id) and table_id:
        gc = pygsheets.authorize(service_file=google_token)
        sh = gc.open_by_key(table_id)

    if sheet_id:
        wk_content = sh.worksheet_by_id(sheet_id)
    else:
        try:
            sh.worksheets('title', sheet_name)
        except:
            sh.add_worksheet(sheet_name)

        wk_content = sh.worksheet_by_title(sheet_name)

    wk_content.set_dataframe(df_data, 'A1', copy_head=True)


def main():
    args = args_parser.arg_parser()
    write_data_to_table(args.csv_path, args.google_token, args.table_id, args.sheet_name)


if __name__ == "__main__":
    main()