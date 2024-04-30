from db.models import ModelBase
from datetime import datetime
from .base import Honeypot, APIRouter
from .base.mixin.docker import DockerMixin
from schema.base import Schema


class Model(Schema):
    content: str
    time: datetime


class DBModel(Model, ModelBase, table=True):
    __tablename__: str = "kippo"


class Kippo(Honeypot[Model, DBModel], DockerMixin):
    router = APIRouter(prefix="/kippo", tags=["kippo"])
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
