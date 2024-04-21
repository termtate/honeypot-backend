from db.models import Base
from datetime import datetime
from .base import Honeypot, APIRouter, Field
from .base.mixin.docker import DockerMixin


class Model(Base):
    content: str
    time: datetime


class DBModel(Model, table=True):
    __tablename__: str = "kippo"

    id: int | None = Field(default=None, primary_key=True, unique=True)


class Kippo(Honeypot[Model, DBModel], DockerMixin):
    router = APIRouter(prefix="/kippo_attacks", tags=["kippo"])
    attack_model = Model
    db_model = DBModel

    docker_config = {"container_name": "kippo"}

    @staticmethod
    def configure_docker_routes(route):
        route.configure_change_container_state("start", "stop")
        route.configure_get_container_state()

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()
