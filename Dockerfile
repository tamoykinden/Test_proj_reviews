FROM python:3.10-slim

# Устанавка зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирую зависимости и устанавливаю их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирую весь проект
COPY . .

# Создаю статик файлы
RUN python manage.py collectstatic --noinput

# Порт приложения
EXPOSE 8000

# Запуск приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]