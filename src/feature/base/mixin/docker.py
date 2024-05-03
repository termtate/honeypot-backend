from __future__ import annotations

from httpx import AsyncClient
from docker.manager import DockerManager
from docker.base import DockerState
from typing import (
    Callable,
    Literal,
    overload,
    Awaitable,
)
from fastapi import APIRouter
from fastapi_injector import Injected
from ..lifespan_context import LifespanContext


class DockerMixin(LifespanContext):
    def __init__(
        self,
        router: APIRouter,
        config: DockerManager.DockerConfig,
        routes: Callable[[Route], list] | None = None,
    ) -> None:
        self.router = router
        self.docker_config = config
        self.docker_manager = DockerManager(**config)
        self.routes = routes
        self.lifespan_events = {self.docker_manager}

    def configure(self):
        route = Route(self)
        if self.routes:
            self.routes(route)


class Route:
    def __init__(self, docker: DockerMixin) -> None:
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
        manager = self.docker.docker_manager

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

                @self.docker.router.post(f"/{state}_container")
                async def container_state():
                    return await manager.configure_docker_state(state)

        else:
            for state in set(states):

                @self.docker.router.post(f"/{state}_container")
                async def container_state():
                    return await manager.configure_docker_state(state)

    def configure_get_container_state(self):
        self.docker.router.get(
            "/container_state",
            response_model=Literal["running", "stopped", "paused"],
        )(self.docker.docker_manager.container_stats)
