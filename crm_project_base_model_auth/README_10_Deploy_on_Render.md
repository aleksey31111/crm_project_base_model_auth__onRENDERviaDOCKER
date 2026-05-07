```markdown
# Развёртывание CRM-проекта на Render (через Docker)

Эта инструкция описывает процесс развёртывания проекта `crm_project_base_model_auth` на платформе Render с использованием Docker. Проект уже подготовлен: есть `Dockerfile`, `requirements.txt`, `docker-compose.yml` (для локальной разработки) и настроен `settings.py` для работы с переменными окружения.

---

## 1. Подготовка проекта для деплоя

### 1.1. Структура репозитория

Убедитесь, что ваш репозиторий на GitHub содержит следующие файлы/папки:

```
crm_project_base_model_auth/
├── Dockerfile
├── requirements.txt
├── manage.py
├── crm_project_base_model_auth/   # пакет с настройками
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── accounts/
├── clients/
├── contracts/
├── tasks/
├── analytics/
├── dashboard/
├── notifications/
├── logs/
├── templates/
├── static/
├── media/
└── ...
```

**Важно:** `Dockerfile` должен лежать в корне репозитория (или вы укажете его путь в настройках Render).

### 1.2. Проверьте `Dockerfile`

Пример рабочего `Dockerfile` (адаптируйте под свой проект):

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Временная база для collectstatic (используется только при сборке)
ENV DATABASE_URL=sqlite:///:memory:
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Запуск: миграции → (опционально создание суперпользователя) → заполнение тестовыми данными → gunicorn
CMD ["sh", "-c", "\
    python manage.py migrate && \
    python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@crm.ru', 'admin123')\" && \
    python manage.py populate_db_docker && \
    gunicorn crm_project_base_model_auth.wsgi:application --bind 0.0.0.0:8000"]
```

### 1.3. Проверьте `requirements.txt`

Убедитесь, что все необходимые библиотеки перечислены. Минимальный набор:

```
Django>=5.1,<5.2
djangorestframework
djangorestframework-simplejwt
drf-spectacular
psycopg2-binary
dj-database-url
whitenoise
gunicorn
celery
redis
python-dotenv
openpyxl
django-filter
Pillow
python-telegram-bot  # если используете телеграм-бота
yookassa             # если нужна интеграция (она идёт как заглушка)
```

### 1.4. Управляющие команды

Если вы планируете загружать тестовые данные, убедитесь, что файл `populate_db_docker.py` лежит в папке `tasks/management/commands/` (можно использовать любое приложение, зарегистрированное в `INSTALLED_APPS`). Структура:

```
tasks/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── populate_db_docker.py
```

---

## 2. Создание базы данных PostgreSQL на Render

1. Войдите в [Render Dashboard](https://dashboard.render.com).
2. Нажмите **New +** → **PostgreSQL**.
3. Укажите имя, например `crm-db`, выберите бесплатный тариф (Free).
4. После создания скопируйте **Internal Database URL** (он понадобится позже).

---

## 3. Создание Web Service (Docker)

1. На панели Render нажмите **New +** → **Web Service**.
2. Подключите ваш GitHub репозиторий.
3. Заполните параметры:

   | Поле | Значение |
   |------|----------|
   | **Name** | `crm-project` (будет частью URL: `crm-project.onrender.com`) |
   | **Environment** | **Docker** (самый важный выбор) |
   | **Branch** | `main` (или ваша основная ветка) |
   | **Root Directory** | (оставьте пустым, если `Dockerfile` лежит в корне репозитория) |
   | **Dockerfile Path** | `./Dockerfile` (по умолчанию) |

4. В разделе **Environment Variables** добавьте переменные (они будут переданы в контейнер):

   | Key | Value |
   |-----|-------|
   | `DEBUG` | `False` |
   | `SECRET_KEY` | `django-insecure-ваш-сложный-ключ` |
   | `ALLOWED_HOSTS` | `crm-project.onrender.com localhost 127.0.0.1` |
   | `CSRF_TRUSTED_ORIGINS` | `https://crm-project.onrender.com` |
   | `BASE_URL` | `https://crm-project.onrender.com` |
   | `DATABASE_URL` | **вставьте скопированный Internal Database URL** |
   | `YOOKASSA_SHOP_ID` | (оставьте пустым) |
   | `YOOKASSA_SECRET_KEY` | (оставьте пустым) |
   | `TELEGRAM_BOT_TOKEN` | (если нужно, иначе пусто) |

5. Поля **Pre-Deploy Command** и **Docker Command** на бесплатном тарифе недоступны (или игнорируются). Всё управление идёт через `Dockerfile`.

6. Нажмите **Create Web Service**.

### 3.1. Важные замечания

- **Root Directory** – если ваш `Dockerfile` лежит не в корне репозитория, укажите путь к папке, содержащей `Dockerfile`. Например, если он находится в `crm_project_base_model_auth/crm_project_base_model_auth/Dockerfile`, а корень репозитория на один уровень выше, то укажите `crm_project_base_model_auth/crm_project_base_model_auth`.
- **Dockerfile** должен выполнять миграции и, при необходимости, заполнять базу тестовыми данными (как в примере выше).
- После создания Render начнёт сборку Docker-образа. Следите за логами на вкладке **Logs**.

---

## 4. Проверка и устранение неполадок

### 4.1. Сайт не открывается (ошибка 400 Bad Request)

**Причина:** отсутствует или неверно задана переменная `ALLOWED_HOSTS`.  
**Решение:** добавьте в **Environment Variables** точное имя домена вашего сервиса (например, `crm-project.onrender.com`).

### 4.2. Не удаётся войти (неверное имя пользователя или пароль)

**Причина:** база данных пуста – нет пользователей.  
**Решение:**  
- Убедитесь, что в `Dockerfile` присутствует создание суперпользователя через `shell` (как в примере).  
- Или выполните команду `python manage.py populate_db_docker` через **One-Off Jobs** (если доступно).  
- Или зайдите в админку `/admin` и создайте пользователя вручную (если админка доступна).

### 4.3. Статика не загружается (нет CSS, JS)

**Причина:** `collectstatic` не выполнился или не настроен `WhiteNoise`.  
**Решение:**  
- В `settings.py` добавьте `whitenoise.middleware.WhiteNoiseMiddleware` в `MIDDLEWARE`.  
- Убедитесь, что `STATIC_ROOT` и `STATICFILES_STORAGE` заданы.  
- В `Dockerfile` перед `CMD` выполните `RUN python manage.py collectstatic --noinput`.

### 4.4. Миграции не применяются

**Причина:** команда `migrate` не включена в `CMD`.  
**Решение:** добавьте `python manage.py migrate` в начало `CMD`.

### 4.5. Ошибка `ModuleNotFoundError: No module named 'yookassa'` (или другая библиотека)

**Причина:** библиотека не указана в `requirements.txt`.  
**Решение:** добавьте её, обновите `requirements.txt`, закоммитьте и передеплойте.

### 4.6. Бесплатный тариф: Shell недоступен

На бесплатном тарифе Render не предоставляет интерактивный Shell. Однако вы можете:

- Использовать **One-Off Jobs** (если доступны).  
- Заложить все необходимые команды в `Dockerfile` (миграции, создание пользователя, заполнение тестовых данных).  
- Временно изменить `CMD`, чтобы выполнить нужные действия, а потом вернуть обратно.

---

## 5. Работа с тестовыми данными

### 5.1. Автоматическое заполнение данных через `Dockerfile`

Если вы включили `python manage.py populate_db_docker` в `CMD`, то при каждом запуске контейнера (в том числе после простоя) база будет заполняться. Скрипт безопасен – использует `get_or_create`, поэтому дублирования не будет.

### 5.2. Однократное заполнение через One-Off Job

1. Перейдите в ваш Web Service → **One-Off Jobs**.
2. Создайте задачу с командой:
   ```bash
   python manage.py populate_db_docker
   ```
3. Запустите её. После успешного выполнения обновите главную страницу – данные появятся.

### 5.3. Ручное заполнение через админку

1. Зайдите в `/admin` (если у вас есть суперпользователь).
2. Создайте несколько клиентов, контрактов, задач вручную. Это самый простой способ для демонстрации, если автоматические скрипты не работают.

---

## 6. После успешного деплоя

- Откройте ваш сайт: `https://crm-project.onrender.com`.
- Войдите с учётными данными:
  - **Логин:** `admin`
  - **Пароль:** `admin123` (если вы создавали через `Dockerfile` или скрипт).
- Проверьте работу разделов: клиенты, контракты, задачи, канбан-доска, аналитика.
- Убедитесь, что статика подгружается (стили, иконки).
- Если планируете использовать платежи – помните, что проект использует **имитацию** (тестовый режим), реальные деньги не списываются.

---

## 7. Обновление приложения

- Внесите изменения в код, закоммитьте и отправьте на GitHub (`git push origin main`).
- Render автоматически пересоберёт Docker-образ и развернёт новую версию (если включён **Auto-Deploy**).
- Если Auto-Deploy выключен, зайдите в **Deploys** → **Manual Deploy** → **Deploy latest commit**.

---

## 8. Полезные ссылки

- [Документация Render (Docker)](https://render.com/docs/deploy-an-existing-docker-image)
- [Django и WhiteNoise](https://whitenoise.readthedocs.io/)
- [Настройка переменных окружения](https://render.com/docs/configure-environment-variables)

---

**Автор:** Aleksey Bashkirov  
**Дата:** май 2026  
**Версия:** 1.0
**Ссылка на render:** https://crm-project-cubu.onrender.com/accounts/login/
**GitHu:** https://github.com/aleksey31111/crm_project_base_model_auth__onRENDERviaDOCKER.git
```