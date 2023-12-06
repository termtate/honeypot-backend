from typing import Type, TypeVar
from source.base import DataSource
from db.crud.base import CRUDWithSession
from aioreactive import AsyncIteratorObserver
from injector import Injector
from logger import Logger
from fastapi_injector import RequestScopeFactory
from expression import curry_flipped
from schema.base import Schema
from db.models.base import Base

TS = TypeVar("TS", bound=Schema)
TM = TypeVar("TM", bound=Base)


@curry_flipped(1)
async def store_attack(
    injector: Injector, source: Type[DataSource[TS]],
    crud: Type[CRUDWithSession[TS, TM]]
):
    s = injector.get(source)
    request_scope_factory = injector.get(RequestScopeFactory)
    logger = injector.get(Logger)

    async for attack in AsyncIteratorObserver(s.stream):
        async with request_scope_factory.create_scope():
            c = injector.get(crud)
            await c.create(attack)
            logger.info(f"stored attack {attack}")
