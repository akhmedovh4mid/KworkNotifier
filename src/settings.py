from pydantic_settings import BaseSettings


class KworkSettings(BaseSettings):
    cookies: dict[str, str]
    favorite_categories: dict[int, list[int]]


class TelegramSettings(BaseSettings):
    bot_token: str
    chat_id: int


class AppSettings(BaseSettings):
    polling_interval: int = 60
