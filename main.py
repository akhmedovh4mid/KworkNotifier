import asyncio
import logging
import signal

from config import app_settings, kwork_settings, telegram_setings
from src.api import KworkAPI
from src.services import ProjectMonitorService
from src.telegram import TelegramClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

shutdown_event = asyncio.Event()


def _signal_handler():
    logging.info("Получен сигнал завершения работы.")
    shutdown_event.set()


async def main():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)
    loop.add_signal_handler(signal.SIGINT, _signal_handler)

    async with KworkAPI(cookies=kwork_settings.cookies) as api:
        async with TelegramClient(telegram_setings.bot_token) as telegram:
            service = ProjectMonitorService(api, telegram, telegram_setings.chat_id)

            while not shutdown_event.is_set():
                try:
                    await service.check_projects()
                except Exception:
                    logging.exception("Ошибка контура мониторинга")

                try:
                    # Ждём либо сигнал завершения, либо таймаут
                    await asyncio.wait_for(
                        shutdown_event.wait(), timeout=app_settings.polling_interval
                    )
                except asyncio.TimeoutError:
                    # Таймаут ожидаем, продолжаем цикл
                    pass       

if __name__ == "__main__":
    asyncio.run(main())
