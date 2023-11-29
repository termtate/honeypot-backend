from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import AsyncIterator, Callable, TypeVar, Concatenate, ParamSpec, Awaitable, overload, Protocol
from .base import Base
from pydantic import BaseModel

T = TypeVar("T")
TMixin = TypeVar("TMixin", bound="CRUDMixin")
P = ParamSpec("P")


class CRUDMixin(Protocol):
    """
    混入CRUD类中，能够给CRUD类增添with_session装饰器
    """
    session: async_sessionmaker[AsyncSession]

    @staticmethod
    @overload
    def with_session(
        func: Callable[Concatenate[TMixin, AsyncSession, P], Awaitable[T]]
    ) -> Callable[Concatenate[TMixin, P], Awaitable[T]]:
        ...

    @staticmethod
    @overload
    def with_session(
        func: Callable[Concatenate[TMixin, AsyncSession, P], AsyncIterator[T]]
    ) -> Callable[Concatenate[TMixin, P], Awaitable[AsyncIterator[T]]]:
        ...

    @staticmethod
    def with_session(
        func: Callable[Concatenate[TMixin, AsyncSession, P],
                       Awaitable[T] | AsyncIterator[T]]
    ) -> Callable[Concatenate[TMixin, P], Awaitable[T | AsyncIterator[T]]]:
        async def wrapper(self: TMixin, *args: P.args, **kwargs: P.kwargs):

            async with self.session.begin() as session:
                res = func(self, session, *args, **kwargs)
                return await res if isinstance(res, Awaitable) else res

        return wrapper


_TS = TypeVar("_TS", bound=BaseModel, contravariant=True)
_TM = TypeVar("_TM", bound=Base, covariant=True)


class CRUDSession(Protocol[_TS, _TM]):
    """
    把CRUDBase里方法的session参数去掉以后的接口
    """
    async def get(
        self,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[_TM]:
        ...

    async def get_by_id(self, id: int) -> _TM | None:
        ...

    async def create(self, schema: _TS) -> _TM:
        ...
