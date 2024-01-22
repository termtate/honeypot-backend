from typing import Protocol, Literal, Final, TypedDict
from httpx import AsyncClient
from pydantic import BaseModel, ConfigDict, Field
from expression import pipe
from core import setting


class ContainerState(BaseModel):
    model_config = ConfigDict(extra="ignore")
    stats: Literal["running", "stopped",
                   "paused"] = Field(validation_alias="Status")


class ContainerInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state: ContainerState


class HoneypotDocker(Protocol):
    docker_base_url: Final = str(setting.DOCKER_REMOTE_API_URL)
    config: "DockerConfig"

    async def start_container(self, client: AsyncClient):
        await client.post(
            f"{self.docker_base_url}/v1.43/containers/{self.config['container_name']}/start"
        )

    async def pause_container(self, client: AsyncClient):
        await client.post(
            f"{self.docker_base_url}/v1.43/containers/{self.config['container_name']}/pause"
        )

    async def unpause_container(self, client: AsyncClient):
        await client.post(
            f"{self.docker_base_url}/v1.43/containers/{self.config['container_name']}/unpause"
        )

    async def stop_container(self, client: AsyncClient):
        await client.post(
            f"{self.docker_base_url}/v1.43/containers/{self.config['container_name']}/stop"
        )

    async def kill_container(self, client: AsyncClient):
        await client.post(
            f"{self.docker_base_url}/v1.43/containers/{self.config['container_name']}/kill"
        )

    async def restart_container(self, client: AsyncClient):
        await client.post(
            f"{self.docker_base_url}/v1.43/containers/{self.config['container_name']}/restart"
        )

    async def container_stats(
        self, client: AsyncClient
    ) -> Literal["running", "stopped", "paused"]:
        return pipe(
            (
                await client.get(
                    f"{self.docker_base_url}/v1.43/containers/{self.config['container_name']}/json"
                )
            ).content,
            ContainerInfo.model_validate_json,
        ).state.stats

    class DockerConfig(TypedDict):
        container_name: str
