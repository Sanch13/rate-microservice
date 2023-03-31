Предпологается, что git и python установлены:
Клонируем проект с репозитория git clone https://github.com/Sanch13/rate-microservice
Если poetry не установлен в системе, то вводим в терминале: pip install poetry
Переходим в папку с проектом:
cd rate-microservice
poetry shell
poetry install
cd rate
python manage.py runserver
http://127.0.0.1:8000/ - точка входа с описанием
