from typing import Annotated, Literal
from datetime import datetime
from pydantic import BeforeValidator, ConfigDict
from pydantic_xml import BaseXmlModel, element

Time = Annotated[
    datetime,
    BeforeValidator(lambda s: datetime.strptime(s, "%Y-%m-%d-%H-%M-%S-%f"))]

ProtocolType = Annotated[
    Literal["ICMP", "TCP", "UDP"],
    BeforeValidator(lambda i: {
        "1": "ICMP",
        "6": "TCP",
        "17": "UDP"
    }[i])]


class AttackSchema(BaseXmlModel, tag="Root"):
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

    @classmethod
    def from_str(cls, content):
        return cls.from_xml(content)
