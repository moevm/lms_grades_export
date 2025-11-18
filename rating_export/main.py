#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime
import utils
import logging
from config import Config
from manage_files import create_student_directories
from html_templates import generate_from_base_html

logger = logging.getLogger("root")

if os.environ.get("LOG_FILE"):
    logging.basicConfig(
        level=logging.INFO,
        filename=os.environ.get("LOG_FILE"),
        filemode="w"
    )
else:
    logging.basicConfig(level=logging.INFO)


class StudentRatingsToDokuWiki:
    def __init__(self, config_path):
        self.config = Config.from_json(config_path)
        self.client = utils.get_client(self.config.google.credentials_file)

    def export_tables(self):
        for table_info in self.config.export:
            students_data = self.export_selected_columns(**table_info.__dict__)
            create_student_directories(
                students_data, base_directory=table_info.outdir_path
            )

            # Генерируем индексную страницу и страницу обновления
            self.generate_index_page(students_data, table_info.outdir_path)

            logger.info(f"Экспортировано страниц студентов: {len(students_data)}")

    def export_selected_columns(
        self,
        spreadsheet_key,
        worksheet_name,
        subject,
        common_columns,
        published_columns,
        outdir_path,
        header_row=0,
    ):
        logger.info(
            f"Старт обработки предмета '{subject}', таблица '{spreadsheet_key}', лист '{worksheet_name}'"
        )
        worksheet = utils.get_worksheet(self.client, spreadsheet_key, worksheet_name)
        # TODO: get диапазона вместо get_all_values http://docs.gspread.org/en/latest/api/models/worksheet.html#gspread.worksheet.Worksheet.get
        data = worksheet.get_all_values()
        headers = data[header_row] if data else []
        self.headers = headers

        # Основные столбцы - ФИО, логин, группа
        name_col = utils.parse_column_specifier(common_columns.get("name"), headers)
        login_col = utils.parse_column_specifier(common_columns.get("login"), headers)
        group_col = utils.parse_column_specifier(common_columns.get("group"), headers)

        # Столбцы для публикации
        if isinstance(published_columns, str):
            published_indices = utils.parse_column_range(published_columns, headers)
        else:
            published_indices = []
            for col_spec in published_columns:
                published_indices.extend(utils.parse_column_range(col_spec, headers))

        published_indices = sorted(set(published_indices))

        # Названия публикуемых столбцов
        published_headers = [headers[i] for i in published_indices if i < len(headers)]

        students_data = []

        for row in data[header_row+1:]:
            if not row or not row[name_col] or not row[login_col] or not row[group_col]:
                continue

            # Основные данные студента
            student_name = utils.extract_from_fio(row[name_col])
            student_login = row[login_col] if len(row) > login_col else None
            student_group = row[group_col] if len(row) > group_col else None

            # Создание ID студента (хэша от логина)
            hash_login = utils.generate_hash(student_login)

            # Извлечение данных из выбранных колонок
            row_data = []
            for col_idx in published_indices:
                if col_idx < len(row):
                    row_data.append(utils.clean_cell_content(row[col_idx]))
                else:
                    row_data.append("")

            # Генерируем страницу
            logger.info(
                f"\tСоздание страницы студента '{student_name}', группа '{student_group}', логин '{student_login}', ID '{hash_login}'"
            )
            filepath = self.generate_student_page(
                student_name,
                hash_login,
                published_headers,
                row_data,
                student_login,
                student_group,
                subject,
                outdir_path,
            )

            students_data.append(
                {
                    "name": student_name,
                    "login": student_login,
                    "group": student_group,
                    "hash": hash_login,
                    "filepath": filepath,
                }
            )

        return students_data

    def generate_student_page(
        self,
        student_name,
        hash_login,
        published_headers,
        row_data,
        student_login,
        student_group,
        subject,
        outdir_path,
    ):
        # Создание содержимого страницы
        html_content = f"""
    <div class="header">
        <h1>🎓 {student_name}</h1>
        <p>Персональная страница студента по дисциплине {subject}</p>
    </div>
    
    <div class="content">
        <div class="card">
            <h2>📋 Основная информация</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">👥 Группа:</span>
                    <span class="info-value">{student_group}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">🔑 Логин:</span>
                    <span class="info-value">{student_login}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Последнее обновление:</span>
                    <span class="info-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>⭐ Рейтинг</h2>
            
            <table>
                <tr>
                    <th>Компонент</th>
                    <th>Значение</th>
                </tr>
    """

        for component, text in zip(published_headers, row_data):
            display_component = utils.clean_cell_content(component)
            score_display = text
            html_content += f"""
                <tr>
                    <td><strong>{display_component}</strong></td>
                    <td><span class="rating-badge">{score_display}</span></td>
                </tr>
        """

        html_content += """
            </table>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="./index.html" class="btn">📁 Мои рейтинги</a>
        </div>
    </div>
    <div class="footer">
        <p>© 2025 Кафедра МОЭВМ | Автоматизированная система рейтинга</p>
    </div>"""

        # У каждого студента своя папка, в которой страницы под каждый предмет
        namespace_path = os.path.join(outdir_path, hash_login)
        if not os.path.exists(namespace_path):
            os.makedirs(namespace_path)
        filename = f"{subject}.html"
        filepath = os.path.join(namespace_path, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(
                generate_from_base_html(
                    f"{student_name} - Рейтинг - {subject}", html_content
                )
            )

        logger.info(
            f"\t\tСоздана страница студента {student_name} для предмета {subject} (путь: {filepath})"
        )

        return filepath

    def generate_index_page(self, students_data, output_dir):
        """Генерация индексной страницы со списком студентов"""

        # Сортируем студентов по группе и имени
        sorted_students = sorted(students_data, key=lambda x: (x["group"], x["name"]))
        
        content = """
        <div class="header">
            <h1>Страницы студенческих рейтингов</h1>
        </div>
        <div class="card">
            <table class="students-table">
                <thead>
                    <tr>
                        <th>№</th>
                        <th>Студент</th>
                        <th>Группа</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, student_data in enumerate(sorted_students, 1):
            student_name = student_data["name"]
            hash_login = student_data["hash"]
            group = student_data["group"]
            
            student_link = f"{hash_login}/index.html"
            
            content += f"""
                    <tr>
                        <td class="number">{i}</td>
                        <td class="student-name">
                            <a href="{student_link}" class="student-link">{student_name}</a>
                        </td>
                        <td class="group">{group}</td>
                    </tr>
            """
        
        content += """
                </tbody>
            </table>
            
            <div class="statistics">
                <h3>Статистика</h3>
                <p>Всего студентов: {total_students}</p>
            </div>
        </div>
        """.format(total_students=len(students_data))

        # Сохраняем индексную страницу
        index_path = os.path.join(output_dir, "moevm_all_student_secret_page_2025.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(generate_from_base_html('Все студенты каф. МОЭВМ', content))

        logger.info(f"Создана индексная страница: {index_path}")


if __name__ == "__main__":
    CONFIG_FILE = "config.json"
    exporter = StudentRatingsToDokuWiki(CONFIG_FILE)
    students_data = exporter.export_tables()
