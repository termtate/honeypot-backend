from datetime import datetime
from typing import Literal
from fastapi import APIRouter
from fastapi_injector import Injected, RequestScopeFactory
from injector import Injector
from db import AsyncSession
from db.crud import CRUDBase
from source.base import DataSource
from db.models import ModelBase
from sqlmodel import select, col


class MainAttackModel(ModelBase, table=True):
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    protocol: str
    type: str
    foreign_id: int


source = DataSource(MainAttackModel)


crud = CRUDBase(MainAttackModel)


async def store(injector: Injector):
    async for attack in source:
        async with injector.get(RequestScopeFactory).create_scope():
            await crud.create(injector.get(AsyncSession), attack)


router = APIRouter(prefix="/main", tags=["main"])


@router.get("/")
async def main_stream(
    offset: int | None = None,
    limit: int | None = None,
    source_ip: str | None = None,
    dest_ip: str | None = None,
    source_port: int | None = None,
    dest_port: int | None = None,
    protocol: Literal["tcp", "udp", "icmp"] | None = None,
    type: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    session: AsyncSession = Injected(AsyncSession),
) -> list[MainAttackModel]:
    stmt = select(MainAttackModel).order_by(col(MainAttackModel.time))

    if source_ip:
        stmt = stmt.where(MainAttackModel.source_ip == source_ip)

    if dest_ip:
        stmt = stmt.where(MainAttackModel.dest_ip == dest_ip)

    if source_port:
        stmt = stmt.where(MainAttackModel.source_port == source_port)

    if dest_port:
        stmt = stmt.where(MainAttackModel.dest_port == dest_port)

    if protocol:
        stmt = stmt.where(MainAttackModel.protocol == protocol)

    if type:
        stmt = stmt.where(MainAttackModel.type == type)

    if from_date:
        stmt = stmt.where(MainAttackModel.time >= from_date)

    if to_date:
        stmt = stmt.where(MainAttackModel.time <= to_date)

    stmt = stmt.offset(offset).limit(limit)

    return [_ async for _ in await session.stream_scalars(stmt)]
