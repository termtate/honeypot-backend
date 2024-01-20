from typing_extensions import Unpack
from .base import HoneypotDocker
from feature.utils import lifespan_scope
from contextlib import AbstractAsyncContextManager
from httpx import AsyncClient


@lifespan_scope
class DockerManager(HoneypotDocker, AbstractAsyncContextManager):
    client: AsyncClient

    def __init__(self, **config: Unpack[HoneypotDocker.DockerConfig]) -> None:
        self.config = config

    async def __aenter__(self):
        self.client = await AsyncClient().__aenter__()

    async def __aexit__(self, __exc_type, __exc_value, __traceback):
        await self.client.__aexit__(__exc_type, __exc_value, __traceback)
