import pygsheets


def read_ids_from_table(google_token, table_id, sheet_id, column_number):
    if google_token and sheet_id and table_id:
        gc = pygsheets.authorize(service_file=google_token)
        sh = gc.open_by_key(table_id)

    try:
        sh.worksheets('title', sheet_id)
    except Exception:
        sh.add_worksheet(sheet_id)

    wk_content = sh.worksheet_by_title(sheet_id)

    return wk_content.get_col(column_number, include_tailing_empty=False)


def cut_lines(lines: [str], skip=0):
    prefixes = ('https://g.dev/', 'https://developers.google.com/profile/u/')
    new_lines = lines[skip:]
    for i, line in enumerate(new_lines):
        for prefix in prefixes:
            if line.startswith(prefix):
                new_lines[i] = line[len(prefix) :]
    return new_lines


def write_data_to_table(df_data, google_token, table_id, sheet_id):
    df_data = df_data.sort_values(by='Joined the Google Developer Program')

    if google_token and sheet_id and table_id:
        gc = pygsheets.authorize(service_file=google_token)
        sh = gc.open_by_key(table_id)

    try:
        sh.worksheets('title', sheet_id)
    except Exception:
        sh.add_worksheet(sheet_id)

    wk_content = sh.worksheet_by_title(sheet_id)

    wk_content.set_dataframe(df_data, 'A1', copy_head=True)
