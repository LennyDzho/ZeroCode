# GenAI WebApp

GenAI — это веб-приложение на Django с Telegram WebApp-интерфейсом и Telegram-ботом на aiogram. Система позволяет пользователям создавать проекты и вести диалоги с языковыми моделями. Предусмотрена поддержка нескольких моделей, ролей пользователей и встроенной панели администратора для управления моделью.

---

## Функциональность

* Авторизация через Telegram WebApp
* Поддержка проектов и вложенных диалогов
* Возможность добавлять участников в проекты
* Сохранение истории сообщений
* Поддержка редактирования сообщений
* Механизм памяти модели (история диалога передаётся в LLM)
* Указание описания проекта влияет на поведение модели
* Поддержка нескольких LLM-поставщиков через OpenRouter


---

## Поведение модели

Если в проекте указано описание, оно используется как инструкция для LLM (C диалогами так не работает). Это позволяет задавать роль или ограничения в диалоге.

Рекомендованная модель: `google/gemini-2.0-flash-exp:free`. Но OpenRouter может выдавать `RateLimit`, поэтому рекомендуется использовать личные ключи.

---

## База данных

По умолчанию используется **SQLite**. Если нужна PostgreSQL, она поддерживается в docker-compose:

```bash
DATABASE_URL=postgres://postgres:postgres@db:5432/genai
```

---

## Установка (Django + бот)

```bash
git clone https://github.com/your-username/genai.git
cd genai
python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate для Windows
pip install -r requirements.txt
cp .env.example .env
```

Запуск:

```bash
python manage.py migrate
python manage.py runserver
python bot.py
```

---

## Docker

```bash
docker-compose up --build
```
От админки данные: admin/admin
В .env настроите:

```
BOT_TOKEN=your-token
WEBAPP_URL=https://your-domain/
```



