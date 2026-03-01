import asyncio
import html
import logging
from typing import Any

from curl_cffi import AsyncSession

from src.models import Want
from src.utils.retry import async_retry

logger = logging.getLogger(__name__)


class TelegramClient:
    BASE_URL = "https://api.telegram.org"

    def __init__(self, bot_token: str) -> None:
        self.bot_token = bot_token
        self.session = AsyncSession(timeout=15)

    @async_retry((Exception,), retries=3)
    async def send_want(self, want: Want, chat_id: int | str) -> dict[str, Any]:
        url = f"{self.BASE_URL}/bot{self.bot_token}/sendMessage"

        safe_description = html.escape(want.description)
        safe_name = html.escape(want.name)

        payload = {
            "chat_id": chat_id,
            "text": (
                f"🔔 Новый проект\n\n"
                f'<a href="{want.url}">{safe_name}</a>\n'
                f"💰 {want.price_limit} руб.\n\n"
                f"{safe_description}"
            ),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        response = await self.session.post(url, json=payload)

        if response.status_code == 429:
            data = response.json()
            retry_after = data.get("parameters", {}).get("retry_after", 3)
            logger.warning(
                "Ограничение скорости в Telegram. Время сна %s сек.",
                retry_after,
            )
            await asyncio.sleep(retry_after)
            raise Exception("Скорость ограничена")

        response.raise_for_status()
        logger.info("Проект %s отправлен", want.id)
        return response.json()

    async def close(self) -> None:
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()
