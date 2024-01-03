from sqlalchemy.ext.asyncio import session
from sqlmodel.ext.asyncio.session import AsyncSession
import asyncio
from contextlib import suppress
from fastapi_injector import request_scope


@request_scope
class SessionContextManager(session._AsyncSessionContextManager[AsyncSession]):
    async def __aexit__(self, __exc_type, __exc_value, __traceback):
        with suppress(asyncio.CancelledError):  # 不屏蔽的话退出的时候会报错
            return await super().__aexit__(
                __exc_type, __exc_value, __traceback
            )