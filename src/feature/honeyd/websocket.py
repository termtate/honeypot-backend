from ..utils import WebsocketManager, inject_constructor
from .schema import AttackSchema
from injector import singleton
from .source import HoneydSource
from logger import Logger
from core import Settings


@singleton
@inject_constructor
class HoneydWebsocket(WebsocketManager[AttackSchema]):
    source: HoneydSource
    logger: Logger
    setting: Settings