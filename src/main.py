from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager, AsyncExitStack
from injector import Injector
from core import setting
from fastapi_injector import (
    attach_injector,
    InjectorMiddleware,
    RequestScopeOptions,
)
from db import DBModule
from feature import (
    api_router,
    configure_main,
    configure_routes,
    lifespan_events,
)


# https://fastapi.tiangolo.com/zh/advanced/events/#lifespan
@asynccontextmanager
async def lifespan(app: FastAPI, injector: Injector):
    await configure_main(injector)

    async with AsyncExitStack() as stack:
        for event in lifespan_events:
            await stack.enter_async_context(event)

        yield


# https://github.com/matyasrichter/fastapi-injector#usage
def make_app(injector: Injector) -> FastAPI:
    app = FastAPI(lifespan=lambda app: lifespan(app, injector))

    app.include_router(api_router, prefix=setting.API_V1_STR)
    app.add_middleware(InjectorMiddleware, injector=injector)

    attach_injector(app, injector, RequestScopeOptions(enable_cleanup=True))
    return app


# https://injector.readthedocs.io/en/latest/terminology.html#injector
injector = Injector([DBModule()])
configure_routes()
app = make_app(injector)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
