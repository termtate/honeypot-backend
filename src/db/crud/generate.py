from typing import ClassVar, TypeVar, Type, AsyncIterator, Generic
from pydantic import BaseModel
from .base import CRUDBase
from ..models.base import Base
from .session import SessionMixin
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod

TSchema = TypeVar("TSchema", bound=BaseModel)
TModel = TypeVar("TModel", bound=Base)

_TS = TypeVar("_TS", bound=BaseModel, contravariant=True)
_TM = TypeVar("_TM", bound=Base, covariant=True)


class CRUDWithSession(ABC, Generic[_TS, _TM]):
    @abstractmethod
    async def get(self, offset: int | None,
                  limit: int | None) -> AsyncIterator[_TM]:
        ...

    @abstractmethod
    async def get_by_id(self, id: int) -> _TM | None:
        ...

    @abstractmethod
    async def create(self, schema: _TS) -> _TM:
        ...


def generate_crud(
    schema: Type[TSchema],
    model: Type[TModel],
):
    class _CRUD(CRUDWithSession, SessionMixin):
        crud: ClassVar = CRUDBase[schema, model](model)

        @SessionMixin.with_session
        def get(
            self,
            session: AsyncSession,
            offset: int | None,
            limit: int | None,
        ):
            return self.crud.get(session, offset, limit)

        @SessionMixin.with_session
        def get_by_id(self, session: AsyncSession, id: int):
            return self.crud.get_by_id(session, id)

        @SessionMixin.with_session
        def create(self, session, schema: schema):
            return self.crud.create(session, schema)

    return _CRUD
