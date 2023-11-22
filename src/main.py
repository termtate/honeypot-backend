import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sockets.manager import SocketsManager
from injector import Injector
from sockets.di import SocketsManagerModule
from core import Settings
from api.api_v1.api import api_router
from fastapi_injector import attach_injector
from logger import LoggerModule
from db import store_attacks_to_db, DBModule


# https://fastapi.tiangolo.com/zh/advanced/events/#lifespan
@asynccontextmanager
async def lifespan(app: FastAPI, injector: Injector):
    sockets_manager = injector.get(SocketsManager)
    # https://stackoverflow.com/questions/76142431/how-to-run-another-application-within-the-same-running-event-loop
    sockets_manager.open_connections()
    asyncio.create_task(injector.call_with_injection(store_attacks_to_db))

    yield

    sockets_manager.close_connections()


# https://github.com/matyasrichter/fastapi-injector#usage
def make_app(injector: Injector) -> FastAPI:
    app = FastAPI(lifespan=lambda app: lifespan(app, injector))

    settings = injector.get(Settings)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    attach_injector(app, injector)
    return app


# https://injector.readthedocs.io/en/latest/terminology.html#injector
injector = Injector([SocketsManagerModule(), LoggerModule(), DBModule()])

app = make_app(injector)
