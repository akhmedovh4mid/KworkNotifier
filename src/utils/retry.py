import asyncio
import logging
from typing import Callable, Type

logger = logging.getLogger(__name__)


def async_retry(
    exceptions: tuple[Type[Exception], ...],
    retries: int = 3,
    base_delay: float = 1.0,
):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == retries:
                        logger.error("Превышено максимальное количество попыток: %s", e)
                        raise

                    logger.warning(
                        "Повторите попытку %s/%s после ошибки: %s",
                        attempt,
                        retries,
                        e,
                    )
                    await asyncio.sleep(delay)
                    delay *= 2  # экспоненциальная задержка

        return wrapper

    return decorator
