from db.models import Base
from datetime import datetime
from .base import Honeypot, APIRouter, Field


class Model(Base):
    content: str
    time: datetime


class DBModel(Model, table=True):
    __tablename__: str = "kippo"

    id: int | None = Field(default=None, primary_key=True, unique=True)


class Kippo(Honeypot[Model, DBModel]):
    router = APIRouter(prefix="/kippo_attacks", tags=["kippo"])
    attack_model = Model
    ModelInDB = DBModel

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()
