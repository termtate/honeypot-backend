from __future__ import annotations
from functools import cache

from httpx import AsyncClient
from docker.manager import DockerManager
from typing import (
    Callable,
    Protocol,
    ClassVar,
    Type,
    Literal,
    cast,
    overload,
    Awaitable,
    TypeVar,
)
from fastapi import APIRouter
from feature.utils.lifespan_scope import lifespan_scope
from fastapi_injector import Injected


class DockerMixin(Protocol):
    docker_config: ClassVar[DockerManager.DockerConfig]
    router: ClassVar[APIRouter]

    @classmethod
    @property
    @cache
    def ContainerManager(cls) -> Type[DockerManager]:
        @lifespan_scope
        class _ContainerManager(DockerManager):
            config: ClassVar = cls.docker_config

        return _ContainerManager

    # def __init_subclass__(cls) -> None:
    #     cls.configure_docker()

    @classmethod
    def configure(cls):
        ...

    @classmethod
    def configure_docker(cls):
        route = Route(cls)
        cls.configure_docker_routes(route)

    @staticmethod
    def configure_docker_routes(route: Route):
        ...


T = TypeVar("T", bound=DockerMixin)


class Route:
    def __init__(self, docker: Type[T]) -> None:
        self.docker = docker

    def _with_docker_manager_parameter_in(
        self, func: Callable[[DockerManager, AsyncClient], Awaitable]
    ):
        async def docker_api(
            manager: DockerManager = Injected(
                self.docker.ContainerManager  # type: ignore
            ),
        ):
            return await func(manager, manager.client)

        return docker_api

    @overload
    def configure_change_container_state(self, states: Literal["all"], /):
        ...

    @overload
    def configure_change_container_state(
        self,
        *states: Literal[
            "start",
            "stop",
            "pause",
            "unpause",
            "restart",
            "kill",
        ],
    ):
        ...

    def configure_change_container_state(self, *states):
        ContainerManager = cast(
            Type[DockerManager],
            self.docker.ContainerManager,  # type: ignore
        )
        mapping = {
            k: self._with_docker_manager_parameter_in(v)
            for k, v in {
                "start": ContainerManager.start_container,
                "stop": ContainerManager.stop_container,
                "pause": ContainerManager.pause_container,
                "unpause": ContainerManager.unpause_container,
                "restart": ContainerManager.restart_container,
                "kill": ContainerManager.kill_container,
            }.items()
        }
        if states == ("all", ):
            for state in mapping:
                self.docker.router.post(f"/{state}_docker")(mapping[state])

        else:
            for state in set(states):
                self.docker.router.post(f"/{state}_docker")(mapping[state])

    def configure_get_container_state(self):
        ContainerManager = cast(
            Type[DockerManager],
            self.docker.ContainerManager,  # type: ignore
        )
        self.docker.router.get(
            "/docker_state",
            response_model=Literal["running", "stopped", "paused"],
        )(
            self._with_docker_manager_parameter_in(
                ContainerManager.container_stats
            )
        )
