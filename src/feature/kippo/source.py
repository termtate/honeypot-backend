from .schema import AttackSchema
from logger import Logger
from schema.socket import Socket
from ..utils import lifespan_scope, SocketSource
from ..utils import inject_constructor


@lifespan_scope
@inject_constructor
class KippoSource(SocketSource[AttackSchema]):
    schema = AttackSchema
    socket = Socket(ip="localhost", port=8123)
    logger: Logger
