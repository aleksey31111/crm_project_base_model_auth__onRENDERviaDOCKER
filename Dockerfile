FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем проект
COPY . .

# Временно задаём фиктивную БД только для сбора статики
ENV DATABASE_URL=sqlite:///:memory:

# Собираем статику
RUN python manage.py collectstatic --noinput

# Удаляем фиктивную переменную (необязательно, но для чистоты)
# ENV DATABASE_URL=

EXPOSE 8000
# Вместо одной команды CMD, запускаем миграции и затем сервер

CMD ["sh", "-c", "\
    python manage.py migrate && \
    python manage.py populate_db_docker && \
    gunicorn crm_project_base_model_auth.wsgi:application --bind 0.0.0.0:8000"]