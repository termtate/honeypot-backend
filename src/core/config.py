from pydantic_settings import BaseSettings
from injector import singleton
from src.schema.socket import Socket


@singleton
class Settings(BaseSettings):
    sockets: list[Socket] = []
    API_V1_STR: str = "/api/v1"