from .schema import AttackSchema
from logger import Logger
from ..utils import lifespan_scope
from ..utils import inject_constructor
from source.base import DataSource


@lifespan_scope
@inject_constructor
class KippoSource(DataSource[AttackSchema]):
    schema = AttackSchema
    logger: Logger

    async def receive_data_forever(self):
        pass