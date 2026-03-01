# 🚀 Монитор проектов Kwork

Асинхронный Python-бот для мониторинга новых проектов на Kwork и отправки уведомлений в Telegram.

Бот автоматически:

* Проверяет новые проекты в избранных категориях
* Отправляет уведомления в Telegram с безопасным HTML-форматированием
* Отмечает проекты как просмотренные
* Поддерживает асинхронную отправку сообщений, retry и экспоненциальную задержку
* Работает циклично с настраиваемым интервалом

---

## ⚡ Возможности

* Полностью async (`asyncio` + `curl_cffi`)
* Retry + exponential backoff для устойчивости к ошибкам
* Rate-limit и timeout защита для Telegram и Kwork API
* Фильтрация проектов по избранным категориям
* Безопасная отправка сообщений с экранированием HTML
* Структурированное логирование
* Готов к Docker и продакшену

---

## 📁 Структура проекта

```
.
├── config.py              # Конфигурация приложения
├── LICENSE
├── main.py                # Точка входа
├── pyproject.toml
├── README.md
└── src
    ├── api.py             # Kwork API client
    ├── models.py          # Data models (Want)
    ├── services.py        # Бизнес-логика мониторинга
    ├── settings.py        # Pydantic настройки
    ├── telegram.py        # Async Telegram client
    └── utils
        └── retry.py       # Retry + exponential backoff
```

---

## ⚙️ Требования

* Python 3.11+
* Аккаунт на Kwork
* Telegram Bot Token

---

## 🔐 Настройка

### 1️⃣ Telegram Bot

1. Создайте нового бота через `@BotFather`
2. Получите `bot_token`
3. Получите `chat_id` через отправку сообщения боту:

```bash
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

---

### 2️⃣ Cookies Kwork

1. Авторизуйтесь на Kwork
2. Откройте DevTools → Application → Cookies
3. Скопируйте cookies и добавьте в `config.py`

> В продакшене рекомендуется хранить cookies в `.env` или переменных окружения, чтобы не коммитить секреты.

---

### 3️⃣ ID категорий

1. Перейдите в Настройки → Избранные категории
2. Измените категории и сохраните
3. В запросах DevTools найдите `/user_favourite_categories/save`
4. В `Response` будут ID категорий и атрибутов, например:

```json
{
  "status": "success",
  "data": {
    "favourite_categories": [41],
    "favourite_attributes": [211, 3587, 7352]
  }
}
```

---

### 4️⃣ Конфигурация через Pydantic

`src/settings.py` разделяет конфиги по секциям:

```python
from pydantic_settings import BaseSettings

class KworkSettings(BaseSettings):
    cookies: dict[str, str]
    favorite_categories: dict[int, list[int]]

class TelegramSettings(BaseSettings):
    bot_token: str
    chat_id: int

class AppSettings(BaseSettings):
    polling_interval: int = 60
```

`config.py` инициализирует объекты:

```python
from src.settings import AppSettings, KworkSettings, TelegramSettings

kwork_settings = KworkSettings(
    cookies={...},
    favorite_categories={41: [211, 3587, 7352]},
)

telegram_settings = TelegramSettings(
    bot_token="YOUR_BOT_TOKEN",
    chat_id=YOUR_CHAT_ID,
)

app_settings = AppSettings(polling_interval=60)
```

---

## ▶️ Запуск

```bash
python main.py
```

Логи выводятся в консоль.
Бот работает циклично с интервалом из `app_settings.polling_interval`.

---

## 🧠 Как работает

1. Обновляет избранные категории через Kwork API
2. Запрашивает новые проекты `/projects`
3. Проверяет поле `dateView`
4. Если проект новый — отправляет уведомление в Telegram
5. После успешной отправки отмечает проект как просмотренный
6. Повторяет цикл каждые `polling_interval` секунд

---

## 📦 Используемые технологии

* `asyncio`
* `curl_cffi` (async HTTP)
* `dataclasses` / `TypedDict`
* `pydantic_settings` для конфигурации
* Retry + exponential backoff
* Структурированное логирование

---

## 📜 License

MIT
