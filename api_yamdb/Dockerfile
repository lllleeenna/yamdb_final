# Создать образ на основе базового слоя python
FROM python:3.9-slim

#Сделать директорию рабочей
WORKDIR /app

COPY requirements.txt .

# Выполнить установку зависимостей внутри контейнера
RUN pip3 install -r requirements.txt --no-cache-dir

# Скопировать с локального компьютера в /app
COPY  . .

#Выполнить запуск сервера разработки при старте контейнера
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]