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


# router = APIRouter(prefix="/kippo", tags=["kippo"])


class Kippo(Honeypot[Model, DBModel]):
    router = APIRouter(prefix="/kippo", tags=["kippo"])
    attack_model = Model
    db_model = DBModel

    docker_config = DockerMixin(
        router,
        config={"container_name": "kippo"},
        routes=lambda r: [
            r.configure_change_container_state("start", "stop"),
            r.configure_get_container_state(),
        ],
    )

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()
