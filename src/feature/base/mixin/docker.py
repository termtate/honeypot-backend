from __future__ import annotations
from functools import cache

from .base import Mixin
from httpx import AsyncClient
from docker.manager import DockerManager
from docker.base import DockerState
from typing import (
    Callable,
    ClassVar,
    Protocol,
    Type,
    Literal,
    cast,
    overload,
    Awaitable,
)
from typing_extensions import Self
from fastapi import APIRouter
from feature.utils.lifespan_scope import lifespan_scope
from fastapi_injector import Injected


class DockerMixin(Mixin, Protocol):
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

    @classmethod
    def configure_mixin(cls, honeypot: Type[Self]):
        route = Route(honeypot)
        honeypot.configure_docker_routes(route)

    @staticmethod
    def configure_docker_routes(route: Route):
        raise NotImplementedError


class Route:
    def __init__(self, docker: Type[DockerMixin]) -> None:
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

        state: DockerState

        if states == ("all",):
            for state in (
                "start",
                "stop",
                "pause",
                "unpause",
                "kill",
                "restart",
            ):
                self.docker.router.post(f"/{state}_container")(
                    self._with_docker_manager_parameter_in(
                        lambda m, c: ContainerManager.configure_docker_state(
                            m, c, state
                        )
                    )
                )

        else:
            for state in set(states):
                self.docker.router.post(f"/{state}_container")(
                    self._with_docker_manager_parameter_in(
                        lambda m, c: ContainerManager.configure_docker_state(
                            m, c, state
                        )
                    )
                )

    def configure_get_container_state(self):
        ContainerManager = cast(
            Type[DockerManager],
            self.docker.ContainerManager,  # type: ignore
        )
        self.docker.router.get(
            "/container_state",
            response_model=Literal["running", "stopped", "paused"],
        )(
            self._with_docker_manager_parameter_in(
                ContainerManager.container_stats
            )
        )
