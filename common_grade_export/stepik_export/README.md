# Grades Parser

## Инструкция по запуску скрипта.

Сначала следует установить все необходимые зависимости: 

``` pip3 install -r requirements.txt ```

Чтобы получить данные в файл csv следует прописать:

``` python3 stepik_parser.py --client_id "Your client id" --client_secret "Your client secret" --url https://stepik.org:443/api --course_id "Your course id" --class_id "Your class id" --csv_path grades ```


Получение данных и в файл, и в Google таблицу:

``` python3 stepik_parser.py --client_id "Your client id" --client_secret "Your client secret" --url https://stepik.org:443/api --course_id "Your course id" --class_id "Your class id" --csv_path grades --google_token "Path to your google token" --table_id "Your table id" [--sheet_name "Name of sheet"] ```

Получение данных и в файл, и на Яндекс Диск:

```python3 grades_parser.py grades_parser --moodle_token "your token" --url http://e.moevm.info --course_id "your course id"[,"id",..] --csv_path grades --yandex_token "Your yandex token" --yandex_path grades```

Получение ``` .json ``` файла для google_token будет описано ниже.

## Инструкция по сборке и запуску Docker контейнера.

Убедитесь, что вместе с исходным кодом лежит ``` .json ``` файл, необходимый для google_token.

Создание докер образа:

``` docker build --tag stepik_grades_parser . ```

Запуск докер контейнера с параметрами:

``` docker run -v "Path to your google token":/app/ --rm stepik_parser.py --client_id "Your client id" --client_secret "Your client secret" --url https://stepik.org:443/api --course_id "Your course id" --class_id "Your class id" --csv_path grades --google_token "Path to your google token" --table_id "Your table id" [--sheet_name "Name of sheet"] ```


## Получение Stepik Токена.

Не являясь администратором можно получить client_id и client_secret.

Для этого нужно перейти по ссылке  https://stepik.org/oauth2/applications/
и выставить параметры client type = confidential, authorization grant type = client credentials.

После нажатия кнопки "Cохранить" ключами можно будет пользоваться.


## Получение токена для работы с Google таблицей.

Сначала нужно создать проект на сайте [Google Cloud](https://console.cloud.google.com/). Выбираем название проекта, жмем на кнопку "Create". 

Затем в меню слева нажимаем на API'S & Services, выбираем Enabled APIs & services. Затем на новой страничке сверху находим "+" с надписью ENABLE APIS AND SERVICES. В поиске находим sheet, нажимаем на кнопку enable, такое же можно сделать и для drive. Теперь приложение может общаться с помощью API Google sheets.

В меню слева в API'S & Services переходим на вкладку Credentials, сверху должен быть восклицательный знак в оранжевом треугольнике, в этом сообщении нажимаем на CONFIGURE CONSENT SCREEN. Выбираем external и жмем Create. Заполняем поля со звездочками, жмем SAVE AND CONTINUE. 

Заходим опять в Credentials. Нажимаем сверху на "+" CREATE CREDENTIALS и выбираем Service account. На первом этапе создаем имя,;жмем continue, на втором даем себе права owner, жмем DONE.

В таблице Service Accounts будет запись, нажимаем на нее. Сверху будет вкладка keys. Add key -> Create new key -> json -> create. Получаем нужный json файл.


## Получение токена для работы с Yandex Disk.

1. Необходимо создать приложение на [Yandex Приложения](https://oauth.yandex.ru/client/new).
       В доступе к данным необходимо указать "Чтение всего диска" и "Запись в любом месте на диске", поле URL заполнить произвольно, например: ```http://127.0.0.1:123/test```.
2. Чтобы получить токен, необходимо скопировать client_id и перейти по ссылке вида 
       ```https://oauth.yandex.ru/authorize?response_type=token&client_id=<идентификатор приложения>``` и скопировать access_token из появившегося на экране запроса.


## Как подключиться к таблице, которая может дать права редактора для определенной почты.

В полученном json файле есть почта некоторого формата, если в гугл таблице дать право редактора этой почте, приложение будет сохранять данные в таблицу.





