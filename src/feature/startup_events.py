import asyncio
from typing import Awaitable, Callable
from injector import Injector

from .honeyd import store_attacks_to_db

startup_events: list[Callable[[Injector], Awaitable]] = [
    store_attacks_to_db,
]


async def _start_startup_events(injector):
    await asyncio.gather(*[func(injector) for func in startup_events])


def start_startup_events(injector: Injector):
    asyncio.create_task(_start_startup_events(injector))
