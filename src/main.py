from fastapi import FastAPI
from contextlib import asynccontextmanager
from injector import Injector
from core import setting
from fastapi_injector import (
    attach_injector,
    InjectorMiddleware,
    RequestScopeOptions,
)
from logger import LoggerModule
from db import DBModule
from feature import (
    honeypot_binds,
    LifespanScope,
    lifespan_scope,
    api_router,
    all_honeypots,
)
from source.base import DataSource


# https://fastapi.tiangolo.com/zh/advanced/events/#lifespan
@asynccontextmanager
async def lifespan(app: FastAPI, injector: Injector):
    scope = injector.get(LifespanScope)
    lifespan_scope.start_startup_events(injector)

    for honeypot in all_honeypots:
        injector.get(DataSource[honeypot.db_model], scope=LifespanScope)

    yield

    await scope.aclose()


# https://github.com/matyasrichter/fastapi-injector#usage
def make_app(injector: Injector) -> FastAPI:
    app = FastAPI(lifespan=lambda app: lifespan(app, injector))

    app.include_router(api_router, prefix=setting.API_V1_STR)
    app.add_middleware(InjectorMiddleware, injector=injector)
    attach_injector(app, injector, RequestScopeOptions(enable_cleanup=True))
    return app


# https://injector.readthedocs.io/en/latest/terminology.html#injector
injector = Injector([LoggerModule(), DBModule()] + honeypot_binds)
app = make_app(injector)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
