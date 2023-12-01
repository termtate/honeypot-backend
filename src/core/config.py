from pydantic_settings import BaseSettings
from injector import singleton
from datetime import timedelta
from pydantic import PostgresDsn


@singleton
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    WEBSOCKET_BUFFER_SEND_INTERVAL: timedelta = timedelta(seconds=5)

    SQLALCHEMY_DATABASE_URI: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        host="localhost",
        username="postgres",
        password="123456",
        # path="test"  # 哪个数据库
    )
