from db.models import ModelBase, Field
from datetime import datetime

from .base import Honeypot, APIRouter
from .base.mixin.docker import DockerMixin
from fastapi_injector import Injected
from db.crud import CRUDWithSession
from schema.base import Schema


class Model(Schema):
    request: str
    slave_id: int
    function_code: int
    response: str
    time: datetime
    session_id: str


class DBModel(Model, ModelBase, table=True):
    __tablename__: str = "conpot"

    id: int | None = Field(default=None, primary_key=True, unique=True)


class Conpot(Honeypot[Model, DBModel], DockerMixin):
    router = APIRouter(prefix="/conpot", tags=["conpot"])
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


@Conpot.router.get("/analysis1")
async def analysis():
    """
    给honeypot增加接口的示例
    """
    return {}


@Conpot.router.get("/analysis2")
async def analysis_with_data_source(
    database: CRUDWithSession[DBModel] = Injected(Conpot.CRUD)
):
    return [item async for item in database.get()]
