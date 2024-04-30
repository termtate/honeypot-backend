from db.models import ModelBase, Field
from datetime import datetime
from schema.base import Schema
from .base import Honeypot, APIRouter


class Model(Schema):
    time: datetime
    protocol: str = Field(schema_extra={"examples": ["ICMP", "TCP", "UDP"]})
    source_port: int | None
    dest_port: int | None
    source_ip: str
    dest_ip: str
    content: str


class DBModel(Model, ModelBase, table=True):
    __tablename__: str = "real_honeypot"


class RealHoneypot(Honeypot[Model, DBModel]):
    router = APIRouter(prefix="/real_honeypot", tags=["real_honeypot"])
    attack_model = Model
    db_model = DBModel

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()
