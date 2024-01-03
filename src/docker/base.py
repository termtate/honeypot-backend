from aiodocker import Docker
from aiodocker.docker import DockerContainer
from typing import Protocol, overload, Literal, AsyncGenerator, Final, TypedDict
from contextlib import AbstractAsyncContextManager


class HoneypotDocker(AbstractAsyncContextManager, Protocol):
    docker: Final[Docker] = Docker()
    container: DockerContainer

    async def start_container(self):
        await self.container.start()

    async def pause_container(self):
        await self.container.pause()

    async def unpause_container(self):
        await self.container.unpause()

    async def stop_container(self):
        await self.container.stop()

    async def kill_container(self):
        await self.container.kill()

    async def restart_container(self):
        await self.container.restart()

    @overload
    async def container_stats(
        self,
        *,
        stream: Literal[True],
    ) -> AsyncGenerator[list, None]:
        ...

    @overload
    async def container_stats(self, *, stream: Literal[False]) -> list:
        ...

    def container_stats(self, *, stream: bool):
        return self.container.stats(stream=stream)

    # async def __aenter__(self):
    #     self.container = await self.docker.containers.get("")

    # async def __aexit__(self, __exc_type, __exc_value, __traceback):
    #     await self.docker.close()

    class DockerConfig(TypedDict):
        container_name: str