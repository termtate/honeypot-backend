from abc import abstractmethod, ABC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncIterator, Type, TypeVar, Generic
from pydantic import BaseModel
from db.models.base import Base

TSchema = TypeVar("TSchema", bound=BaseModel)
TModel = TypeVar("TModel", bound=Base)


class CRUD(ABC, Generic[TSchema, TModel]):
    @abstractmethod
    async def get(
        self,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[TModel]:
        pass

    @abstractmethod
    async def get_by_id(self, session: AsyncSession, id: int) -> TModel | None:
        pass

    @abstractmethod
    async def create(self, session: AsyncSession, schema: TSchema) -> TModel:
        pass


class CRUDBase(CRUD[TSchema, TModel]):
    def __init__(self, model: Type[TModel]) -> None:
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[TModel]:
        stmt = select(self.model)\
            .order_by(self.model.id)\
            .offset(offset)\
            .limit(limit)
        stream = await session.stream_scalars(stmt)
        async for row in stream:
            yield row

    async def get_by_id(self, session: AsyncSession, id: int) -> TModel | None:
        stmt = select(self.model).where(self.model.id == id)
        return await session.scalar(stmt)

    async def create(self, session: AsyncSession, schema: TSchema) -> TModel:
        a = self.model(**schema.model_dump())
        session.add(a)
        await session.flush()
        new = await self.get_by_id(session, a.id)
        assert new is not None
        return new