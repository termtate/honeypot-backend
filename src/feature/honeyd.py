from typing import Annotated, Literal
from db.models import Base, Field
from datetime import datetime
from .base import Honeypot, APIRouter

from pydantic import BeforeValidator, ConfigDict, ValidationError
from pydantic_xml import BaseXmlModel, element
from schema import Socket
from .utils import start_server, catch
from .base.mixin.docker import DockerMixin

Time = Annotated[
    datetime,
    BeforeValidator(lambda s: datetime.strptime(s, "%Y-%m-%d-%H-%M-%S-%f")),
]

ProtocolType = Annotated[
    Literal["ICMP", "TCP", "UDP"],
    BeforeValidator(lambda i: {"1": "ICMP", "6": "TCP", "17": "UDP"}[i]),
]


class XmlModel(BaseXmlModel, tag="Root"):
    model_config = ConfigDict(from_attributes=True)

    symbol: int = element(tag="SYMBOL")
    alert_type: int = element(tag="AlertType")
    subtype: int = element(tag="SubType")
    time: Time = element(tag="Time")
    protocol: ProtocolType = element(tag="Proto")
    source_port: int = element(tag="sPort")
    dest_port: int = element(tag="dPort")
    connection_begin_time: Time = element(tag="ConnectBeginTime")
    time_stamp: int = element(tag="receiveTime")
    pack_length: int = element(tag="PacketLen")
    source_ip: str = element(tag="ip_src")
    dest_ip: str = element(tag="ip_dst")


class Model(Base):
    symbol: int
    alert_type: int
    subtype: int
    time: datetime
    protocol: str = Field(schema_extra={"examples": ["ICMP", "TCP", "UDP"]})
    source_port: int
    dest_port: int
    connection_begin_time: datetime
    time_stamp: int
    pack_length: int
    source_ip: str
    dest_ip: str

    @classmethod
    def from_str(cls, content):
        return cls.model_validate(XmlModel.from_xml(content))


class DBModel(Model, table=True):
    __tablename__: str = "honeyd"

    id: int | None = Field(default=None, primary_key=True, unique=True)


class Honeyd(Honeypot[Model, DBModel], DockerMixin):
    router = APIRouter(prefix="/honeyd_attacks", tags=["honeyd"])
    attack_model = Model
    db_model = DBModel

    docker_config = {"container_name": "honeyd"}

    @staticmethod
    def configure_docker_routes(route):
        route.configure_change_container_state("all")
        route.configure_get_container_state()

    @staticmethod
    def configure_routes(route) -> None:
        route.configure_get_attacks()
        route.configure_create_attack()
        route.configure_send_attack_with_websocket()

    @staticmethod
    async def receive_data_forever(source):
        socket = Socket(ip="localhost", port=8123)
        source.logger.info(f"start listening socket on {socket}")
        return await start_server(
            socket=socket,
            on_receive=catch(ValidationError)(source.add)(
                on_exception=lambda e: source.logger.warning(
                    f"validate error: {e.json(indent=2, include_url=False)}"
                )
            ),
        )
