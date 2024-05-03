from db.models import ModelBase, Field
from datetime import datetime

from .base import Honeypot, APIRouter
from .base.mixin.docker import DockerMixin
from fastapi_injector import Injected
from schema.base import Schema
from db import AsyncSession


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


class Conpot(Honeypot[Model, DBModel]):
    router = APIRouter(prefix="/conpot", tags=["conpot"])
    attack_model = Model
    db_model = DBModel

    docker_config = DockerMixin(
        router,
        config={"container_name": "conpot"},
        routes=lambda r: [
            r.configure_change_container_state("all"),
            r.configure_get_container_state(),
        ],
    )

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
async def analysis_with_crud(
    session: AsyncSession = Injected(AsyncSession),
) -> list[DBModel]:
    """
    给honeypot增加接口的示例，且有数据库查询
    """
    return [item async for item in Conpot.crud.get(session)]
