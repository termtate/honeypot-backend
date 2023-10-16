from pydantic_settings import BaseSettings

from src.schema.socket import Socket


class Settings(BaseSettings):
    sockets: list[Socket] = []
    API_V1_STR: str = "/api/v1"