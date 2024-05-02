from datetime import datetime
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, col
from typing import AsyncIterator, Type, TypeVar, Generic
from db.models.base import ModelBase

TModel = TypeVar("TModel", bound=ModelBase)


class CRUDBase(Generic[TModel]):
    """增删改查的基本实现"""

    def __init__(self, model: Type[TModel]) -> None:
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[TModel]:
        stmt = (
            select(self.model)
            .order_by(col(self.model.id).desc())
            .offset(offset)
            .limit(limit)
        )
        stream = await session.stream_scalars(stmt)
        async for row in stream:
            yield row

    async def get_by_id(
        self, session: AsyncSession, id: int | None
    ) -> TModel | None:
        stmt = select(self.model).where(self.model.id == id)
        return await session.scalar(stmt)

    async def get_by_time(
        self,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ):
        if to_date is None:
            to_date = datetime.now()
        stmt = (
            select(self.model)
            .order_by(col(self.model.time))
            .where(
                (from_date <= self.model.time) & (self.model.time <= to_date)
                if from_date is not None
                else self.model.time <= to_date
            )
            .offset(offset)
            .limit(limit)
        )

        async for row in await session.stream_scalars(stmt):
            yield row

    async def create(self, session: AsyncSession, model: TModel) -> TModel:
        session.add(model)
        await session.flush()
        await session.refresh(model)
        return model
