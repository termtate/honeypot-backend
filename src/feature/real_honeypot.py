from db.models import Base, Field
from datetime import datetime

from .base import Honeypot, APIRouter


class Model(Base):
    time: datetime
    protocol: str = Field(schema_extra={"examples": ["ICMP", "TCP", "UDP"]})
    source_port: int | None
    dest_port: int | None
    source_ip: str
    dest_ip: str
    content: str


class DBModel(Model, table=True):
    __tablename__: str = "real_honeypot"

    id: int | None = Field(default=None, primary_key=True, unique=True)


class RealHoneypot(Honeypot[Model, DBModel]):
    router = APIRouter(prefix="/real_honeypot", tags=["real_honeypot"])
    attack_model = Model
    db_model = DBModel

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()
