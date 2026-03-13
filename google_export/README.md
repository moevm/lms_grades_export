# developer.google.com badges Parser

## Инструкция по запуску скрипта

- -o | --output - название выходного csv файла
- -i | --ids_file - список id пользователей (файл c id разделенные переносами строки, могут быть как строками, так и числовыми значениями, значения строк будут в столбце name в выходном файле)
- -k | --key - ключ для экспорта badge'й (брал из dev консоли браузера в запросе, отфильтровав по badges и get запросам (параметр key в конце строки))
- -c | --curl_args - ключ для нахождения id пользователя, если оно представляется как строковое (аналогично предыдущему, фильтровать по GetProfile, POST-запрос, ключ в header'ах 'X-Goog-Api-Key').
- -t | --timeout - таймаут 1 запроса
- -r | --repeat - количество повторных отправок запроса (10 - по умолчнию)

### По аналогии с соседними экспортерами:
- --google_token - путь до токена для выгрузки в гугл таблицы
- --table_id - id гугл-таблицы
- --sheet_id - НАЗВАНИЕ листа в гугл таблице

- --yandex_token - токен для яндекс таблиц
- --yandex_path путь на яндекс диске

### Вместо загрузки id из файлов можно использовать импорт из гугл-таблиц
- --input_sheet_id - НАЗВАНИЕ листа в гугл таблице
- --input_column_number - номер колонки (например 'B' - 2)
- --input_column_skip - количество элементов чтобы пропустить

Пример:
```bash
python3 main.py -o 'fname.csv' -k 'ключ1' -c 'ключ2' --google_token "токен" --table_id id_таблицы --sheet_id=out --input_sheet_id=in --input_column_number=2 --input_column_skip=3 -t 2
```

```bash
python3 main.py -i 'ids' -o 'fname.csv' -k 'ключ1' -c 'ключ2' -t 0.1
```
### Для запуска через докер

```bash
docker build -t gd_exporter:latest .
```

```bash
docker run -it --entrypoint python3 gd_exporter main.py -i 'ids' -o 'fname.csv' -k 'ключ1' -c 'ключ2' -t 0.1"
```
