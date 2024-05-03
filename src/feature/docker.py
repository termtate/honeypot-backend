from datetime import datetime
from pydantic import BaseModel, Field, TypeAdapter, ConfigDict, computed_field
from fastapi import APIRouter, HTTPException
from aiodocker import Docker
from typing import Any, Literal, TypeVar, Type, Generic
from core import setting
from expression import curry
from collections.abc import Sequence
import aiodocker
import httpx

T = TypeVar("T")
TL = TypeVar("TL", bound=Sequence)

docker = Docker()


class Response(BaseModel, Generic[TL]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    list: TL

    @computed_field
    def total(self) -> int:
        return len(self.list)


@curry(1)
async def get(type: Type[T], path, **params) -> T:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{setting.DOCKER_REMOTE_API_URL}{path}", params=params
        )
        match type:
            case BaseModel():
                return type.model_validate_json(res.content)
            case _:
                return TypeAdapter(type).validate_json(res.content)


@curry(1)
async def get_list(type: Type[TL], path, **params) -> Response[TL]:
    return Response(list=await get(type)(path, **params))


class Port(BaseModel):
    IP: str | None
    PrivatePort: int
    PublicPort: int
    Type: Literal["tcp", "udp", "sctp"]


# https://docs.docker.com/engine/api/v1.45/#tag/Container/operation/Containerlist
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
    SizeRw: int | None = None
    SizeRootFs: int | None = None
    HostConfig: dict[str, str]
    NetworkSettings: dict[str, Any]
    Mounts: list[dict[str, Any]]


router = APIRouter(prefix="/docker", tags=["docker"])


@router.get("/containers", response_model=Response[list[Container]])
async def all_containers():
    return Response(
        list=[_._container for _ in await docker.containers.list(all=True)]
    )


class ContainerCreate(BaseModel):
    Hostname: str = ""
    Domainname: str = ""
    User: str = ""
    Env: list[str] = Field(default_factory=list)
    Cmd: list[str] = Field(default_factory=list)
    Image: str
    Volumes: dict[str, Any] | None = None
    WorkingDir: str = ""
    Entrypoint: list[str] = Field(default_factory=list)
    HostConfig: dict[str, Any] = Field(default_factory=dict)
    NetworkingConfig: dict[str, Any] = Field(default_factory=dict)


class CreateContainerResponse(BaseModel):
    id: str


@router.post("/containers", response_model=CreateContainerResponse)
async def create_container(name: str, data: ContainerCreate):
    try:
        return (
            await docker.containers.create(config=data.model_dump(), name=name)
        )._container
    except aiodocker.exceptions.DockerError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


class State(BaseModel):
    Status: Literal[
        "created",
        "running",
        "paused",
        "restarting",
        "removing",
        "exited",
        "dead",
    ]
    Running: bool
    Paused: bool
    Restarting: bool
    OOMKilled: bool
    Dead: bool
    Pid: int
    ExitCode: int
    Error: str
    StartedAt: datetime
    FinishedAt: datetime


class RestartPolicy(BaseModel):
    Name: str
    MaximumRetryCount: int


class HostConfig(BaseModel):
    Binds: Any
    ContainerIDFile: str
    LogConfig: Any
    NetworkMode: str
    PortBindings: dict[str, Any]
    RestartPolicy: RestartPolicy
    AutoRemove: bool
    VolumeDriver: str
    VolumesFrom: Any
    ConsoleSize: list[int]
    CapAdd: list[str]
    CapDrop: Any
    CgroupnsMode: str
    Dns: list
    DnsOptions: list
    DnsSearch: list
    ExtraHosts: Any
    GroupAdd: Any
    IpcMode: str
    Cgroup: str
    Links: Any
    OomScoreAdj: int
    PidMode: str
    Privileged: bool
    PublishAllPorts: bool
    ReadonlyRootfs: bool
    SecurityOpt: Any
    UTSMode: str
    UsernsMode: str
    ShmSize: int
    Runtime: str
    Isolation: str
    CpuShares: int
    Memory: int
    NanoCpus: int
    CgroupParent: str
    BlkioWeight: int
    BlkioWeightDevice: list
    BlkioDeviceReadBps: list
    BlkioDeviceWriteBps: list
    BlkioDeviceReadIOps: list
    BlkioDeviceWriteIOps: list
    CpuPeriod: int
    CpuQuota: int
    CpuRealtimePeriod: int
    CpuRealtimeRuntime: int
    CpusetCpus: str
    CpusetMems: str
    Devices: list
    DeviceCgroupRules: Any
    DeviceRequests: Any
    MemoryReservation: int
    MemorySwap: int
    MemorySwappiness: Any
    OomKillDisable: bool
    PidsLimit: Any
    Ulimits: Any
    CpuCount: int
    CpuPercent: int
    IOMaximumIOps: int
    IOMaximumBandwidth: int
    MaskedPaths: list[str]
    ReadonlyPaths: list[str]


class Config(BaseModel):
    Hostname: str
    Domainname: str
    User: str
    AttachStdin: bool
    AttachStdout: bool
    AttachStderr: bool
    Tty: bool
    OpenStdin: bool
    StdinOnce: bool
    Env: list[str]
    Cmd: list[str]
    Image: str
    Volumes: Any
    WorkingDir: str
    Entrypoint: Any
    OnBuild: Any
    Labels: dict[str, Any]


class Bridge(BaseModel):
    IPAMConfig: Any
    Links: Any
    Aliases: Any
    NetworkID: str
    EndpointID: str
    Gateway: str
    IPAddress: str
    IPPrefixLen: int
    IPv6Gateway: str
    GlobalIPv6Address: str
    GlobalIPv6PrefixLen: int
    MacAddress: str
    DriverOpts: Any


class Networks(BaseModel):
    bridge: Bridge


class NetworkSettings(BaseModel):
    Bridge: str
    SandboxID: str
    HairpinMode: bool
    LinkLocalIPv6Address: str
    LinkLocalIPv6PrefixLen: int
    Ports: dict[str, Any]
    SandboxKey: str
    SecondaryIPAddresses: Any
    SecondaryIPv6Addresses: Any
    EndpointID: str
    Gateway: str
    GlobalIPv6Address: str
    GlobalIPv6PrefixLen: int
    IPAddress: str
    IPPrefixLen: int
    IPv6Gateway: str
    MacAddress: str
    Networks: Networks


class ContainerInfo(BaseModel):
    Id: str
    Created: str
    Path: str
    Args: list[str]
    State: State
    Image: str
    ResolvConfPath: str
    HostnamePath: str
    HostsPath: str
    LogPath: str
    Name: str
    RestartCount: int
    Driver: str
    Platform: str
    MountLabel: str
    ProcessLabel: str
    AppArmorProfile: str
    ExecIDs: list[str] | None
    HostConfig: HostConfig
    GraphDriver: Any
    Mounts: list
    Config: Config
    NetworkSettings: NetworkSettings


@router.get("/containers/{id_or_name}", response_model=ContainerInfo)
async def container_info(id_or_name: str):
    return await docker.containers.container(id_or_name).show()


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
