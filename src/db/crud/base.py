from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col
from typing import AsyncIterator, ClassVar, Type, TypeVar, Generic, Protocol
from db.models.base import Base

TModel = TypeVar("TModel", bound=Base)


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
            select(self.model).order_by(col(self.model.id).desc()
                                        ).offset(offset).limit(limit)
        )
        stream = await session.stream_scalars(stmt)
        async for row in stream:
            yield row

    async def get_by_id(
        self, session: AsyncSession, id: int | None
    ) -> TModel | None:
        stmt = select(self.model).where(self.model.id == id)
        return await session.scalar(stmt)

    async def create(self, session: AsyncSession, model: TModel) -> TModel:
        session.add(model)
        await session.flush()
        await session.refresh(model)
        return model


class CRUDWithSession(Protocol[TModel]):
    """
    将`CRUDBase`的方法里的session参数提升到了构造参数，以便依赖注入

    >>> @request_scope
    >>> @inject_constructor
    >>> class MyCRUD(CRUDWithSession[MyModel]):
    >>>     crud = CRUDBase(MyModel)
    >>>     session: AsyncSession
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

    async def create(self, model: TModel) -> TModel:
        return await self.crud.create(self.session, model)
