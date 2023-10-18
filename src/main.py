from fastapi import FastAPI
from contextlib import asynccontextmanager
from sockets.manager import SocketsManager
from injector import Injector
from sockets.di import SocketsManagerModule
from core import Settings
from sockets.manager import SocketsManager
import asyncio
from api.api_v1.api import api_router
from fastapi_injector import attach_injector

@asynccontextmanager
async def lifespan(app: FastAPI, injector: Injector):
    sockets_manager = injector.get(SocketsManager)
    # https://stackoverflow.com/questions/76142431/how-to-run-another-application-within-the-same-running-event-loop
    task = asyncio.create_task(sockets_manager.open_connections())

    yield
    
    task.cancel()


def make_app(injector: Injector) -> FastAPI:
    app = FastAPI(lifespan=lambda app: lifespan(app, injector))

    settings = injector.get(Settings)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    attach_injector(app, injector)
    return app

injector = Injector([SocketsManagerModule()])
    
app = make_app(injector)

if __name__ == '__main__':
    import uvicorn
    
    uvicorn.run(app, port=8000)
