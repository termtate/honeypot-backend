from ..utils import WebsocketManager
from .schema import AttackSchema
from fastapi_injector import request_scope
from dataclasses import dataclass
from injector import inject
from .source import HoneydSource
from logger import Logger
from core import Settings


@request_scope
@inject
@dataclass
class HoneydWebsocket(WebsocketManager[AttackSchema]):
    source: HoneydSource
    logger: Logger
    setting: Settings