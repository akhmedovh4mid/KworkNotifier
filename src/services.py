import asyncio
import logging
from typing import Iterable

from src.api import KworkAPI
from src.models import Want
from src.telegram import TelegramClient

logger = logging.getLogger(__name__)


class ProjectMonitorService:
    def __init__(
        self,
        api: KworkAPI,
        telegram: TelegramClient,
        chat_ids: Iterable[int | str],
        concurrency: int = 5,
    ):
        self.api = api
        self.telegram = telegram
        self.chat_ids = list(chat_ids)
        self.semaphore = asyncio.Semaphore(concurrency)

    async def _notify_one(self, want: Want) -> int | None:
        async with self.semaphore:
            try:
                await asyncio.gather(
                    *(
                        self.telegram.send_want(want, chat_id)
                        for chat_id in self.chat_ids
                    )
                )
                return want.id
            except Exception:
                logger.exception("Не удалось уведомить %s", want.id)
                return None

    async def check_projects(self) -> None:
        response = await self.api.get_projects(page=1, view=0)
        wants = [Want.from_dict(w) for w in response["data"]["wants"]]
        new_wants = [w for w in wants if w.date_view is None]

        if not new_wants:
            logger.info("Нет новых проектов")
            return

        results = await asyncio.gather(*(self._notify_one(w) for w in new_wants))

        successful_ids = [r for r in results if r is not None]

        if successful_ids:
            await self.api.mark_viewed(successful_ids)
            logger.info("Отмечено как просмотренное: %s", successful_ids)
