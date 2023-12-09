from .schema import AttackSchema
from logger import Logger
from schema.socket import Socket
from ..utils import lifespan_scope, SocketSource
from ..utils import inject_constructor


@lifespan_scope
@inject_constructor
class ConpotSource(SocketSource[AttackSchema]):
    schema = AttackSchema
    socket = Socket(ip="localhost", port=8234)
    logger: Logger
