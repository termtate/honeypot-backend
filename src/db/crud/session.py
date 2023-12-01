from typing import AsyncIterator, TypeVar, Protocol
from .base import Base
from pydantic import BaseModel

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
