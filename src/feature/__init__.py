import asyncio
from typing import Awaitable

from fastapi import APIRouter
from .docker import router as docker_router, docker
from .conpot import Conpot
from .honeyd import Honeyd
from .kippo import Kippo
from .snap7 import Snap7
from .real_honeypot import RealHoneypot
from .webtrap import Webtrap
from .main import router as main_router, store
from .base.mixin import DockerMixin
from user import api_router as user_router


all_honeypots = [
    Conpot,
    Honeyd,
    Kippo,
    RealHoneypot,
    Webtrap,
    Snap7,
]
api_router = APIRouter()


dockers: list[DockerMixin] = []
mains: list[Awaitable] = []
honeypot_routers = []
lifespan_events = [docker]

for honeypot in all_honeypots:
    honeypot_routers.append(honeypot.router)
    if honeypot.docker_config is not None:
        dockers.append(honeypot.docker_config)
        lifespan_events.extend(honeypot.docker_config.lifespan_events)

    if honeypot.main_stream_config is not None:
        mains.append(honeypot.main_stream_config.configure(honeypot))
        lifespan_events.extend(honeypot.main_stream_config.lifespan_events)


def configure_routes():
    for pot in all_honeypots:
        pot.configure()
        pot.source
        lifespan_events.extend(pot.lifespan_events)

    for d in dockers:
        d.configure()

    for router in honeypot_routers:
        api_router.include_router(router)


api_router.include_router(docker_router)

api_router.include_router(main_router)
api_router.include_router(user_router)


async def configure_main(injector):
    for main in mains:
        await main

    task = asyncio.create_task(store(injector))  # noqa: F841


@api_router.get("/honeypots", tags=["total"])
async def honeypots() -> list[str]:
    return [_.prefix[1:] for _ in honeypot_routers]
