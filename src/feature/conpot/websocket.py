from ..utils import WebsocketManager, inject_constructor
from .schema import AttackSchema
from injector import singleton
from .source import ConpotSource
from logger import Logger
from core import Settings


@singleton
@inject_constructor
class ConpotWebsocket(WebsocketManager[AttackSchema]):
    source: ConpotSource
    logger: Logger
    setting: Settings