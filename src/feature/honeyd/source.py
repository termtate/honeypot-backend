from .schema import AttackSchema
from injector import inject
from logger import Logger
from schema.socket import Socket
from ..utils import lifespan_scope, SocketSource
from .crud import CRUDAttack
from dataclasses import dataclass


@lifespan_scope
@inject
@dataclass
class HoneydSource(SocketSource[AttackSchema]):
    schema = AttackSchema
    socket = Socket(ip="localhost", port=8123)
    logger: Logger
    crud: CRUDAttack
