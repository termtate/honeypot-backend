from fastapi import FastAPI
from contextlib import asynccontextmanager
from injector import Injector
from core import Settings
from feature.api import api_router
from fastapi_injector import attach_injector, InjectorMiddleware, RequestScopeOptions
from logger import LoggerModule
from db import DBModule
from feature import LifespanScope, lifespan_scope


# https://fastapi.tiangolo.com/zh/advanced/events/#lifespan
@asynccontextmanager
async def lifespan(app: FastAPI, injector: Injector):
    scope = injector.get(LifespanScope)
    lifespan_scope.start_startup_events(injector)

    yield

    await scope.aclose()


# https://github.com/matyasrichter/fastapi-injector#usage
def make_app(injector: Injector) -> FastAPI:
    app = FastAPI(lifespan=lambda app: lifespan(app, injector))

    settings = injector.get(Settings)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.add_middleware(InjectorMiddleware, injector=injector)
    attach_injector(app, injector, RequestScopeOptions(enable_cleanup=True))
    return app


# https://injector.readthedocs.io/en/latest/terminology.html#injector
injector = Injector([LoggerModule(), DBModule()])
app = make_app(injector)
