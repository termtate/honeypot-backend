from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import AsyncIterator, Callable, TypeVar, Concatenate, ParamSpec, Awaitable, overload
from injector import inject, singleton

T = TypeVar("T")
TMixin = TypeVar("TMixin", bound="SessionMixin")
P = ParamSpec("P")


@singleton
class SessionMixin:
    @inject
    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self.session = session

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