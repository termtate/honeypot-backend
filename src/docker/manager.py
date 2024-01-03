from typing_extensions import Unpack
from .base import HoneypotDocker
from feature.utils import lifespan_scope


@lifespan_scope
class DockerManager(HoneypotDocker):
    def __init__(self, **config: Unpack[HoneypotDocker.DockerConfig]) -> None:
        self.config = config

    async def __aenter__(self):
        self.container = await self.docker.containers.get(
            self.config['container_name']
        )

    async def __aexit__(self, __exc_type, __exc_value, __traceback):
        await self.docker.close()