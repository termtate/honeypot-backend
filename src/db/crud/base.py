from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from typing import AsyncIterator, ClassVar, Type, TypeVar, Generic, Protocol
from pydantic import BaseModel
from db.models.base import Base
from .session import CRUDMixin, CRUDSession

TSchema = TypeVar("TSchema", bound=BaseModel, contravariant=True)
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


class CRUDWithSession(CRUDSession[TSchema, TModel], CRUDMixin, Protocol):
    """
    把`CRUDBase`方法中的session参数提到了构造函数中
    """
    crud: ClassVar[CRUDBase]
    session: async_sessionmaker[AsyncSession]

    @CRUDMixin.with_session
    def get(
        self,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[TModel]:
        return self.crud.get(session, offset, limit)

    @CRUDMixin.with_session
    async def get_by_id(self, session: AsyncSession, id: int) -> TModel | None:
        return await self.crud.get_by_id(session, id)

    @CRUDMixin.with_session
    async def create(self, session, schema: TSchema) -> TModel:
        return await self.crud.create(session, schema)