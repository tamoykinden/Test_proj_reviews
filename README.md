# Car Reviews API

Django REST Framework API для управления отзывами об автомобилях.

## Технологии

- Python 3.10+
- Django 5.2.6
- Django REST Framework 3.16.1
- PostgreSQL 15
- Docker, Docker Compose

## Функциональность

### Модели данных
- Страны производителей
- Производители автомобилей  
- Модели автомобилей
- Отзывы

### API Endpoints
- CRUD операции для всех моделей
- Экспорт данных в XLSX и CSV форматах
- Токенная аутентификация для изменяющих операций
- Публичный доступ для просмотра и добавления комментариев

### Безопасность
- Изменение данных только по токену
- Валидация входных данных
- Защита от SQL-инъекций

### Инструкция по запуску
1. Создание виртуального окружения
Linux/Mac:
python -m venv venv
source venv/bin/activate

Windows:
venv\Scripts\activate

2. Установка зависимостей
pip install -r requirements.txt

3. Настройка базы данных:

Установите PostgreSQL и создайте базу данных
createdb db_test_task

Применение миграций
python manage.py migrate

4. Создание суперпользователя
python manage.py createsuperuser

5. Запуск сервера
python3 manage.py runserver

6. Проверка работы
Откройте: http://localhost:8000/api/countries/

### Использование API
Аутентификация
Для операций изменения данных (POST, PUT, DELETE) требуется токен доступа. Токен передается в заголовке запроса:

Authorization: ваш_токен

#### Примеры HTTP запросов
Получение списка стран:
GET http://localhost:8000/api/countries/

Создание новой страны (требуется токен):

POST http://localhost:8000/api/countries/
Authorization: Token your_api_access_token_here
Content-Type: application/json

{
  "name": "Германия"
}

Экспорт данных в Excel:
GET http://localhost:8000/api/countries/export/xlsx/

Экспорт данных в CSV:
GET http://localhost:8000/api/countries/export/csv/

Создание комментария (публичный доступ):
POST http://localhost:8000/api/comments/
Content-Type: application/json

{
  "email": "user@example.com",
  "car": 1,
  "comment_text": "Отличный автомобиль!"
}

### Конфигурация
Переменные окружения (.env)
Файл .env в корне проекта со следующими параметрами:

SECRET_KEY=your_django_secret_key_here
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432
API_ACCESS_TOKEN=your_api_access_token_here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

### Docker Compose
Проект использует два сервиса:
web - Django приложение на порту 8000
db - PostgreSQL база данных на порту 5432

### Тестирование
Для тестирования API используйте предоставленный файл requests.http с коллекцией примеров запросов.