from typing import AsyncIterator, TypeVar, Protocol
from .base import ModelBase

_TM = TypeVar("_TM", bound=ModelBase)


class CRUDSession(Protocol[_TM]):
    """
    把CRUDBase里方法的session参数去掉以后的接口
    """

    def get(
        self,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[_TM]:
        ...

    async def get_by_id(self, id: int) -> _TM | None:
        ...

    async def create(self, model: _TM) -> _TM:
        ...
