from pydantic_settings import BaseSettings
from injector import singleton
from schema import Socket, Attack
from schema.attacks.alt import Validator1
from datetime import timedelta

@singleton
class Settings(BaseSettings):
    sockets: list[Socket] = [
        Socket(
            ip="localhost", 
            port=8123, 
            attack_validator=Validator1
        )
    ]
    API_V1_STR: str = "/api/v1"
    
    WEBSOCKET_BUFFER_SEND_INTERVAL: timedelta = timedelta(seconds=5)