from docker.manager import DockerManager
from typing import Protocol, ClassVar, Type, Literal, overload
from fastapi import APIRouter


class Route:
    def __init__(self, docker: Type["DockerMixin"]) -> None:
        self.docker = docker

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
        mapping = {
            "start": self.docker.docker_manager.start_container,
            "stop": self.docker.docker_manager.stop_container,
            "pause": self.docker.docker_manager.pause_container,
            "unpause": self.docker.docker_manager.unpause_container,
            "restart": self.docker.docker_manager.restart_container,
            "kill": self.docker.docker_manager.kill_container
        }
        if states == "all":
            for state in mapping:
                self.docker.router.post(f"/{state}_docker")(mapping[state])

        else:
            for state in tuple(states):
                self.docker.router.post(f"/{state}_docker")(mapping[state])

    def configure_get_container_state(self):
        self.docker.router.get("/docker_state")(
            lambda: self.docker.docker_manager.container_stats(stream=False)
        )


class DockerMixin(Protocol):
    docker_config: ClassVar[DockerManager.DockerConfig]
    docker_manager: ClassVar[DockerManager]
    router: ClassVar[APIRouter]

    def __init_subclass__(cls) -> None:
        cls.configure_docker()

    @classmethod
    def configure_docker(cls):
        cls.docker_manager = DockerManager(**cls.docker_config)
        route = Route(cls)
        cls.configure_docker_routes(route)

    @staticmethod
    def configure_docker_routes(route: Route):
        ...
