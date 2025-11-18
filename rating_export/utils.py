import gspread
import re
import hashlib
from google.oauth2.service_account import Credentials
from datetime import datetime


# =================================== Блок работы с хэшем ===================================


def generate_hash(login, salt="moevm", lenght=10):
    """
    Генерация хэша для "секретного" названия раздела студента (логин + соль)
    """
    return hashlib.sha256((f"{login}:{salt}").encode("utf-8")).hexdigest()[:lenght]


# =================================== Блок работы с google service ===================================


def get_client(credentials_file):
    credentials = Credentials.from_service_account_file(
        credentials_file, scopes=["https://spreadsheets.google.com/feeds"]
    )
    return gspread.authorize(credentials)


def get_worksheet(client, spreadsheet_id, worksheet_name):
    return client.open_by_key(spreadsheet_id).worksheet(worksheet_name)


# =================================== Блок работы с таблицей ===================================


def clean_cell_content(cell_content):
    """
    Очистка содержимого ячейки от переносов строк и лишних пробелов (для заголовков)
    """
    if not cell_content:
        return ""

    return re.sub(r"\s+", " ", cell_content)


def find_login_column(headers, login_columns=("Логин на e.moevm.info", "moodle")):
    """
    Поиск столбца с логином
    """
    for i, header in enumerate(headers):
        if header in login_columns:
            return i
    return None


def find_column_by_name(column_name, headers):
    """
    Поиск колонки по названию в заголовках
    """
    column_name_lower = column_name
    for i, header in enumerate(headers):
        if header and header == column_name_lower:
            return i

    return None


def parse_column_specifier(column_spec, headers):
    """
    Парсинг спецификатора колонки: может быть числом [0;...), названием или буквой
        - вариант с названием проверяется перед буквой из-за особенностей проверки
        - спецификатор-буква - ожидается не длиннее 2х символов (от A до ZZ, т.е. не более ~700 столбцов)
    Возвращает индекс колонки (0-based)
    """
    # Число
    if isinstance(column_spec, int):
        return column_spec

    if isinstance(column_spec, str):
        # Название колонки
        by_name = find_column_by_name(column_spec, headers)
        if by_name is not None:
            return by_name
        elif len(column_spec) < 3:
            # Буква колонки
            return column_letter_to_index(column_spec.upper())

        raise ValueError(f"Колонка '{column_spec}' не найдена в {headers}")
    raise ValueError(
        f"Неподдерживаемый формат ({type(column_spec)}) колонки '{column_spec}'"
    )


def column_letter_to_index(column_letter):
    """
    Конвертация буквы колонки в индекс (A=0, B=1, ..., Z=25, AA=26, ...)
    """
    index = 0
    for char in column_letter:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index - 1


def parse_column_range(range_spec, headers):
    """
    Парсинг диапазона колонок: "A:C", "B-D", "3:5", "ФИО:Группа"
    Возвращает список индексов колонок
    """
    if ":" not in range_spec:
        return [parse_column_specifier(range_spec, headers)]

    start_spec, end_spec = range_spec.split(":", 1)

    start_idx = parse_column_specifier(start_spec.strip(), headers)
    end_idx = parse_column_specifier(end_spec.strip(), headers)

    return list(range(start_idx, end_idx + 1))


# =================================== Блок работы с разным ===================================


def extract_from_fio(full_name):
    full_name = full_name.split(' ')
    return f"{full_name[0]} {full_name[1]}"