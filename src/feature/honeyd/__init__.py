from typing import Awaitable, Callable
from .crud import CRUDAttack
from .source import HoneydSource as HoneydSource
from aioreactive import AsyncIteratorObserver
from injector import inject, Injector
from logger import Logger
from fastapi_injector import RequestScopeFactory


# 为什么这么复杂？
# 因为crud依赖的session属于request_scope，只能在一次请求周期后被提交，
# 所以必须要在RequestScopeFactory.create_scope()创建一个请求周期，然后在内部使用injector.get获取crud，这样才能提交的上去
async def store_attacks_to_db(injector: Injector):

    async def inner(func: Callable[[CRUDAttack, Logger], Awaitable]):
        return await injector.call_with_injection(func)

    return await injector.call_with_injection(_store_attacks_to_db(inner))


def _store_attacks_to_db(
    store: Callable[[Callable[[CRUDAttack, Logger], Awaitable]], Awaitable],
):
    @inject
    async def inner(
        source: HoneydSource,
        request_scope_factory: RequestScopeFactory,
    ):
        async for attack in AsyncIteratorObserver(source.stream):
            async with request_scope_factory.create_scope():
                await store(handle_attack(attack))

    return inner


def handle_attack(attack, ):
    @inject
    async def inner(crud: CRUDAttack, logger: Logger):
        await crud.create(attack)
        logger.info(f"stored {attack=}")

    return inner