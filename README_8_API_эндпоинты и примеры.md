# README: CRM Project `crm_project_base_model_auth`

## Содержание

- [О проекте](#о-проекте)
- [Технологии](#технологии)
- [Установка и запуск](#установка-и-запуск)
  - [Локальный запуск (без Docker)](#локальный-запуск-без-docker)
  - [Запуск через Docker](#запуск-через-docker)
- [Наполнение тестовыми данными](#наполнение-тестовыми-данными)
- [API – эндпоинты и примеры](#api--эндпоинты-и-примеры)
  - [Аутентификация](#аутентификация)
  - [Клиенты](#клиенты)
  - [Контракты](#контракты)
  - [Платежи](#платежи)
  - [Инициация платежа (учебный режим)](#инициация-платежа-учебный-режим)
- [Тестирование](#тестирование)
  - [Запуск тестов для конкретных приложений](#запуск-тестов-для-конкретных-приложений)
- [Примечание о платежах и ЮKassa](#примечание-о-платежах-и-юkassa)
- [Структура проекта](#структура-проекта)

---

## О проекте

Учебная CRM-система для управления клиентами, контрактами, задачами и аналитикой.  
**Ключевые возможности:**
- Управление клиентами (CRUD, типы: юр. лицо, физ. лицо, ИП).
- Контракты с суммами, статусами оплаты, ответственными менеджерами.
- Задачи с приоритетами, сроками, комментариями, канбан‑доской.
- Дашборд с графиками выручки и распределения задач.
- REST API (DRF + JWT) с разграничением прав.
- **Имитация платежей** – без реального подключения к ЮKassa.
- Экспорт в Excel, импорт клиентов из CSV (через Celery).
- Уведомления (внутренние, email) и логирование API.

---

## Технологии

- **Backend:** Python 3.12, Django 5.1, Django REST Framework, Celery
- **База данных:** PostgreSQL 15 (или SQLite для разработки)
- **Кеш/брокер:** Redis
- **Контейнеризация:** Docker, Docker Compose
- **Платежи:** имитация (учебный режим)
- **Экспорт:** openpyxl

---

## Установка и запуск

### Локальный запуск (без Docker)

1. **Клонируйте репозиторий**
   ```bash
   #git clone https://github.com/aleksey31111/crm_project_base_model_auth__Diplom_AI.git
   cd crm_project_base_model_auth
   ```

2. **Создайте виртуальное окружение и активируйте его**
   ```bash
   #python -m venv .venv
   #source .venv/bin/activate   # Linux/Mac
   #.venv\Scripts\activate      # Windows
   ```

3. **Установите зависимости**
   ```bash
   pip install -r requirements_LocalMachine.txt
   ```

4. **Настройте переменные окружения** – создайте файл `.env` в корне:
   ```ini
   DEBUG=1
   SECRET_KEY=your-secret-key
   DB_HOST=localhost
   DB_NAME=crm_db
   DB_USER=crm_user
   DB_PASSWORD=crm_password
   # ЮKassa оставьте пустыми:
   YOOKASSA_SHOP_ID=
   YOOKASSA_SECRET_KEY=
   ```

5. **Выполните миграции**
   ```bash
   python manage.py migrate
   ```

6. **Запустите сервер**
   ```bash
   python manage.py runserver
   ```

### Запуск через Docker

1. **Создайте файл `.env`** (аналогично локальному, но `DB_HOST=db`).
2. **Соберите и запустите контейнеры**
   ```bash
   docker-compose up -d --build
   ```
3. **Выполните миграции**
   ```bash
   docker-compose exec web python manage.py migrate
   ```
4. **Заполните базу тестовыми данными** (см. следующий раздел).
5. **Соберите статику**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```
6. Откройте `http://localhost:8000` в браузере.

---

## Наполнение тестовыми данными

Для быстрого старта подготовлены два скрипта:

- **`populate_db.py`** – для локального запуска.
- **`populate_db_docker.py`** – для Docker (учитывает особенность среды).

Запуск (локально):
```bash
python manage.py populate_db
```
В Docker:
```bash
docker-compose exec web python manage.py populate_db_docker
```

Скрипты создают:
- Пользователей с разными ролями (admin, manager, sales, support, viewer).
- Клиентов (юр. лица, ИП, физ. лица).
- Контракты с суммами, статусами оплаты.
- Платежи (частичные / полные, с фейковыми `yookassa_id`).
- Задачи (с приоритетами, сроками, исполнителями, просроченными).
- Комментарии, отчёты, уведомления.

> **Пароль суперпользователя `admin`:** `admin123`

---

## API – эндпоинты и примеры

### Аутентификация

Используется JWT (Simple JWT).

- **Получение токена**
  ```
  POST /api/token/
  Content-Type: application/json
  {"username": "admin", "password": "admin123"}
  ```
- **Обновление токена**
  ```
  POST /api/token/refresh/
  {"refresh": "<refresh_token>"}
  ```

Все дальнейшие запросы требуют заголовок:
```
Authorization: Bearer <access_token>
```

### Клиенты

Базовый URL: `http://127.0.0.1:8000/api/docs/#/`
```bash
curl.exe -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" -d '{\"username\":\"admin\",\"password\":\"123456\"}'
```
curl.exe -X GET "http://127.0.0.1:8000/api/clients/" -H "Authorization: Bearer access

| Метод | Эндпоинт                | Описание                         |
|-------|-------------------------|----------------------------------|
| GET   | `/api/clients/`         | Список клиентов (с пагинацией)  |
| POST  | `/api/clients/`         | Создание клиента                |
| GET   | `/api/clients/{id}/`    | Детали клиента                  |
| PUT   | `/api/clients/{id}/`    | Полное обновление               |
| PATCH | `/api/clients/{id}/`    | Частичное обновление            |
| DELETE| `/api/clients/{id}/`    | Удаление клиента (если нет контрактов) |

**Фильтрация и поиск:**
- `?type=company` – тип клиента
- `?status=active` – статус
- `?manager=1` – ID менеджера
- `?search=текст` – поиск по названию, ИНН, email, телефону

**Пример создания клиента (юридическое лицо):**
```json
{
  "type": "company",
  "full_name": "ООО Ромашка",
  "inn": "7701234567",
  "phone": "+74951234567",
  "email": "info@romashka.ru"
}
```

### Контракты

Базовый URL: `http://127.0.0.1:8000/api/docs/#/`

```bash
curl.exe -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" -d '{\"username\":\"admin\",\"password\":\"123456\"}'
```
curl.exe -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" -d '{\"username\":\"admin\",\"password\":\"123456\"}'

| Метод | Эндпоинт                 | Описание                         |
|-------|--------------------------|----------------------------------|
| GET   | `/api/contracts/`        | Список контрактов                |
| POST  | `/api/contracts/`        | Создание контракта               |
| GET   | `/api/contracts/{id}/`   | Детали контракта                 |
| PATCH | `/api/contracts/{id}/`   | Обновление                       |
| DELETE| `/api/contracts/{id}/`   | Удаление                         |

**Дополнительные вычисляемые поля в сериализаторе:**
- `remaining_amount` – остаток к оплате
- `payment_percentage` – процент оплаты
- `payments` – список связанных платежей

**Фильтрация:**
- `?status=active` – статус контракта
- `?payment_status=paid` – статус оплаты
- `?type=sale` – тип контракта
- `?client=1` – по ID клиента
- `?manager=2` – по ID менеджера

**Пример создания:**
```json
{
  "client": 1,
  "number": "К-001/2025",
  "title": "Поставка оборудования",
  "type": "sale",
  "amount": "150000.00",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

### Платежи

Базовый URL: `/api/payments/`

| Метод | Эндпоинт                | Описание                         |
|-------|-------------------------|----------------------------------|
| GET   | `/api/payments/`        | Список платежей (админ/менеджер) |
| GET   | `/api/payments/{id}/`   | Детали платежа                  |
| POST  | `/api/payments/`        | Добавление ручного платежа      |
| PUT   | `/api/payments/{id}/`   | Обновление                      |
| DELETE| `/api/payments/{id}/`   | Удаление                        |

### Инициация платежа (учебный режим)

**Эндпоинт:** `/api/contracts/{contract_id}/initiate-payment/`  
**Метод:** `POST`  
**Тело (опционально):**
```json
{
  "amount": 50000.00
}
```
Если `amount` не указан, используется остаток по контракту.

**Ответ:**
```json
{
  "payment_id": "fake_abc123def",
  "confirmation_url": "/fake-payment/1/?amount=50000",
  "amount": "50000.00",
  "status": "pending"
}
```

После получения `confirmation_url` пользователь переходит на эту страницу, нажимает «Подтвердить оплату» (учебная имитация). Система отправляет внутренний вебхук и обновляет статус контракта.

> **Важно:** Реальная ЮKassa не используется. Все платежи – имитация.

---

## Тестирование

Для запуска тестов используется стандартный раннер Django. Все тесты расположены в приложениях `clients/tests/` и `contracts/tests/`.

### Запуск тестов для конкретных приложений

```bash
# Только клиенты
python manage.py test clients --verbosity 2

# Только контракты (включая платежи)
python manage.py test contracts --verbosity 2

# Оба приложения
python manage.py test clients contracts --verbosity 2

# Один конкретный тестовый класс
python manage.py test clients.tests.test_api.ClientAPITest

# Один метод
python manage.py test clients.tests.test_api.ClientAPITest.test_manager_sees_only_own_clients
```

**В Docker:**
```bash
docker-compose exec web python manage.py test clients contracts --verbosity 2
```

> Примечание: тесты не требуют запущенного Celery или реального брокера – они используют синхронное выполнение задач и in‑memory базу данных.

---

## Примечание о платежах и ЮKassa

- **Реальная интеграция отсутствует.** В коде присутствуют заглушки, которые активируются, если переменные `YOOKASSA_SHOP_ID` и `YOOKASSA_SECRET_KEY` не заданы (или пусты).  
- **Вебхук `/contracts/webhook/yookassa/`** принимает любые POST‑запросы (без проверки IP) и обрабатывает события `payment.succeeded` / `payment.canceled` для фейковых платежей.  
- **Для перехода на реальную ЮKassa** необходимо:
  1. Зарегистрироваться и получить `shop_id` и `secret_key`.
  2. Указать их в `.env`.
  3. В `contracts/views.py` раскомментировать вызов `is_allowed_ip()` для проверки IP.
  4. В `contracts/viewsets.py` заменить имитацию на реальный вызов `YooPayment.create()`.

---

## Структура проекта

```
crm_project_base_model_auth/
├── accounts/                # Пользователи, профили, аутентификация
├── analytics/               # Аналитика, отчёты, API графиков
├── clients/                 # Клиенты, импорт/экспорт
├── contracts/               # Контракты, платежи, вебхук, имитация
├── core/                    # Базовые модели, декораторы, контекстные процессоры
├── dashboard/               # Главная панель с графиками
├── logs/                    # Логирование API и вебхуков
├── notifications/           # Уведомления, настройки
├── tasks/                   # Задачи, канбан-доска
├── templates/               # HTML-шаблоны
├── static/                  # CSS, JS
├── utils/                   # Экспорт в Excel
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── populate_db.py / populate_db_docker.py
└── .env
```

---

**Автор:** *Aleksey Bashkirov*  
**Проект:** дипломная работа (учебный)  
**GitHub**: [https://github.com/aleksey31111/crm_project_base_model_auth__Diplom_AI/tree/master ]
**Дата:** апрель 2026