#Базовый образ Python
FROM python:3.12-slim

#Установить рабочую директорию в контейнере
WORKDIR /app

#Скопировать все файлы в рабочую директорию контейнера
COPY . /app

#Установить зависимости
RUN pip install --no-cache-dir -r requirements.txt

#Открыть порт 8000 для работы приложения
EXPOSE 8000

#Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
