from pydantic import BaseModel
from fastapi import APIRouter
import httpx
from typing import Any, Literal
from core import setting


async def get(path):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{setting.DOCKER_REMOTE_API_URL}{path}")
        return res.content


class Port(BaseModel):
    IP: str | None
    PrivatePort: int
    PublicPort: int
    Type: Literal["tcp", "udp", "sctp"]


# https://docs.docker.com/engine/api/v1.45/#tag/Container/operation/ContainerList
class Container(BaseModel):
    Id: str
    Names: list[str]
    Image: str
    ImageID: str
    Command: str
    Created: int
    State: str
    Status: str
    Ports: list[Port]
    Labels: dict[str, str]
    SizeRw: int
    SizeRootFs: int
    HostConfig: dict[str, str]
    NetworkSettings: dict[str, Any]
    Mounts: list[dict[str, Any]]


router = APIRouter(prefix="/docker", tags=["docker"])


@router.get("/containers", response_model=list[Container])
async def all_containers():
    return await get("/containers/json")


class Image(BaseModel):
    Id: str
    ParentId: str
    RepoTags: list[str]
    RepoDigests: list[str]
    Created: str
    Size: int
    SharedSize: int
    VirtualSize: int | None
    Labels: dict[str, str]
    Containers: int


@router.get("/images", response_model=list[Image])
async def all_images():
    return await get("/images/json")
