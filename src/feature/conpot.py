from db.models import Base, Field
from datetime import datetime

from .base import Honeypot, APIRouter
from .base.mixin.docker import DockerMixin


class Model(Base):
    request: str
    slave_id: int
    function_code: int
    response: str
    time: datetime
    session_id: str


class DBModel(Model, table=True):
    __tablename__: str = "conpot"

    id: int | None = Field(default=None, primary_key=True, unique=True)


class Conpot(Honeypot[Model, DBModel], DockerMixin):
    router = APIRouter(prefix="/conpot_attacks", tags=["conpot"])
    attack_model = Model
    db_model = DBModel

    docker_config = {"container_name": "conpot"}

    @staticmethod
    def configure_docker_routes(route):
        route.configure_change_container_state("all")
        route.configure_get_container_state()

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()
