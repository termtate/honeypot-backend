from pydantic import BaseModel, TypeAdapter, ConfigDict, computed_field
from fastapi import APIRouter
import httpx
from typing import Any, Literal, TypeVar, Type, Generic
from core import setting
from expression import curry
from collections.abc import Sequence

T = TypeVar("T")
TL = TypeVar("TL", bound=Sequence)


class Response(BaseModel, Generic[TL]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    list: TL

    @computed_field
    def total(self) -> int:
        return len(self.list)


@curry(1)
async def get(type: Type[T], path) -> T:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{setting.DOCKER_REMOTE_API_URL}{path}")
        match type:
            case BaseModel():
                return type.model_validate_json(res.content)
            case _:
                return TypeAdapter(type).validate_json(res.content)


@curry(1)
async def get_list(type: Type[TL], path) -> Response[TL]:
    return Response(list=await get(type)(path))


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
    Labels: dict[str, str] | None
    SizeRw: int
    SizeRootFs: int
    HostConfig: dict[str, str]
    NetworkSettings: dict[str, Any]
    Mounts: list[dict[str, Any]]


router = APIRouter(prefix="/docker", tags=["docker"])


@router.get("/containers")
async def all_containers() -> Response[list[Container]]:
    return await get_list(list[Container])("/containers/json")


class Image(BaseModel):
    Id: str
    ParentId: str
    RepoTags: list[str]
    RepoDigests: list[str] | None
    Created: int
    Size: int
    SharedSize: int
    VirtualSize: int | None
    Labels: dict[str, str] | None
    Containers: int


@router.get("/images")
async def all_images() -> Response[list[Image]]:
    return await get_list(list[Image])("/images/json")
