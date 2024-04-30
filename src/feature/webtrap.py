from db.models import ModelBase, Field
from .base import Honeypot, APIRouter
from .base.mixin.docker import DockerMixin
from schema.base import Schema


class Model(Schema):
    client_address: str = Field(schema_extra={"examples": ["127.0.0.1"]})

    command: str = Field(
        schema_extra={"examples": ["GET", "POST", "PUT", "DELETE", "PATCH"]}
    )
    path: str = Field(
        schema_extra={"examples": ["/path?para1=val1&para2=val2"]}
    )
    request_version: str = Field(schema_extra={"examples": ["HTTP/1.1"]})
    headers: str = Field(
        schema_extra={
            "examples": ["Accept: application/json, text/javascript"]
        }
    )
    protocol_version: str = Field(schema_extra={"examples": ["HTTP/1.0"]})


class DBModel(Model, ModelBase, table=True):
    __tablename__: str = "webtrap"


class Webtrap(Honeypot[Model, DBModel], DockerMixin):
    router = APIRouter(prefix="/webtrap", tags=["webtrap"])
    attack_model = Model
    db_model = DBModel

    docker_config = {"container_name": "webtrap"}

    @staticmethod
    def configure_docker_routes(route):
        route.configure_change_container_state("all")
        route.configure_get_container_state()

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()
