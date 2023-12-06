from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncIterator, ClassVar, Type, TypeVar, Generic, Protocol
from db.models.base import Base
from .session import CRUDSession
from schema.base import Schema

TSchema = TypeVar("TSchema", bound=Schema, contravariant=True)
TModel = TypeVar("TModel", bound=Base, covariant=True)


class CRUDBase(Generic[TSchema, TModel]):
    """增删改查的基本实现"""
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


class CRUDWithSession(CRUDSession[TSchema, TModel], Protocol):
    """
    把`CRUDBase`方法中的session参数提到了构造函数中
    """
    crud: ClassVar[CRUDBase]
    session: AsyncSession

    def get(
        self,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[TModel]:
        return self.crud.get(self.session, offset, limit)

    async def get_by_id(self, id: int) -> TModel | None:
        return await self.crud.get_by_id(self.session, id)

    async def create(self, schema: TSchema) -> TModel:
        return await self.crud.create(self.session, schema)
