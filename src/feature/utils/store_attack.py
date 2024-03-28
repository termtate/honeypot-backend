from typing import Type, TypeVar
from source.base import DataSource
from db.crud.base import CRUDWithSession
from injector import Injector
from logger import Logger
from fastapi_injector import RequestScopeFactory
from expression import curry_flipped
from db.models.base import Base

TM = TypeVar("TM", bound=Base)


@curry_flipped(1)
async def store_attack(
    injector: Injector,
    source: Type[DataSource[TM]],
    crud: Type[CRUDWithSession[TM]],
):
    s = injector.get(source)
    request_scope_factory = injector.get(RequestScopeFactory)
    logger = injector.get(Logger)

    async for attack in s:
        async with request_scope_factory.create_scope():
            c = injector.get(crud)
            await c.create(attack)
            logger.info(f"stored attack {attack}")
