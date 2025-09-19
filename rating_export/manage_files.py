import os
import glob
from html_templates import generate_from_base_html
import logging


logger = logging.getLogger("root")


def generate_student_index_html(student_data, student_directory):
    """
    Генерирует index.html для студента со списком файлов в его каталоге
    """
    # Получаем список файлов в каталоге студента (исключая сам index.html)
    files = []
    if os.path.exists(student_directory):
        for file_path in glob.glob(os.path.join(student_directory, "*")):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                if filename != "index.html":  # Исключаем сам index.html
                    file_size = os.path.getsize(file_path)
                    files.append(
                        {"name": filename, "size": file_size, "path": filename}
                    )

    # Сортируем файлы по имени
    files.sort(key=lambda x: x["name"])

    html_content = f"""

    <div class="header">
        <h1>🎓 {student_data['name']}</h1>
        <p>Рейтинги дисциплин студента</p>
    </div>
    <div class="content">
    <div class="card">
            <h2>📋 Основная информация</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">👥 Группа:</span>
                    <span class="info-value">{student_data.get('group', 'Не указана')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">🔑 Логин:</span>
                    <span class="info-value">{student_data.get('login', 'Не указан')}</span>
                </div>
            </div>
        </div>

        <h2>📄 Доступные рейтинги:</h2>
        <div class="card">
"""

    if files:
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Дисциплина</th>
                </tr>
            </thead>
            <tbody>
        """

        for file_info in files:
            html_content += f"""
                <tr>
                    <td>
                        <a href="{file_info['path']}" class="file-link">{file_info['name'].rsplit('.', 1)[0]}</a>                        
                    </td>
                </tr>
            """

        html_content += """
            </tbody>
        </table>
        """
    else:
        html_content += """
        <div class="empty-folder">
            <h3>Доступные рейтинги не найдены</h3>
            <p>Нет рейтингов для отображения</p>
        </div>
        """

    html_content += f"""
        <div class="last-update">
            Страница сгенерирована: <span id="generation-time">{get_current_time()}</span>
        </div>
    </div></div>
        <div class="footer">
        <p>© 2025 Кафедра МОЭВМ | Автоматизированная система рейтинга</p>
    </div>
    </div>
</body>
</html>
"""

    return generate_from_base_html(
        f"{student_data['name']} - Рейтинги дисциплин студента", html_content
    )


def get_current_time():
    """Возвращает текущее время в формате строки"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_student_directories(students_data, base_directory):
    """
    Создает каталоги для всех студентов и генерирует index.html
    """
    # Создаем базовый каталог если его нет
    os.makedirs(base_directory, exist_ok=True)

    for student in students_data:
        # Создаем каталог для студента
        student_dir = os.path.join(base_directory, student["hash"])
        os.makedirs(student_dir, exist_ok=True)

        # Генерируем index.html для студента
        index_html = generate_student_index_html(student, student_dir)

        # Сохраняем index.html в каталоге студента
        index_path = os.path.join(student_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)

        logger.info(f"Создан index.html для {student['name']} в {student_dir}")
