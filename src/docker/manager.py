from typing_extensions import Unpack

from src.docker.base import DockerState
from .base import HoneypotDocker
from contextlib import AbstractAsyncContextManager
from httpx import AsyncClient


class DockerManager(HoneypotDocker, AbstractAsyncContextManager):
    client: AsyncClient

    def __init__(self, **config: Unpack[HoneypotDocker.DockerConfig]) -> None:
        self.config = config

    async def configure_docker_state(self, state: DockerState):
        return await super().configure_docker_state(self.client, state)

    async def container_stats(self):
        return await super().container_stats(self.client)

    async def __aenter__(self):
        self.client = await AsyncClient().__aenter__()

    async def __aexit__(self, __exc_type, __exc_value, __traceback):
        await self.client.__aexit__(__exc_type, __exc_value, __traceback)
