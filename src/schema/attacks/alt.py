from datetime import datetime
from typing import Annotated, ClassVar, Mapping
from pydantic_xml import BaseXmlModel, element
from pydantic.functional_validators import BeforeValidator
from .attack import AttackSchema
from abc import ABC, abstractmethod
from typing_extensions import override, Self


class AttackValidator(ABC):
    @classmethod
    @abstractmethod
    def validate(cls, content: bytes) -> Self:
        pass

    @abstractmethod
    def to_attack(self) -> AttackSchema:
        pass


Time = Annotated[
    datetime,
    BeforeValidator(lambda s: datetime.strptime(s, "%Y-%m-%d-%H-%M-%S-%f"))]


class Validator1(AttackValidator, BaseXmlModel, tag="Root"):
    symbol: int = element(tag="SYMBOL")
    alert_type: int = element(tag="AlertType")
    subtype: int = element(tag="SubType")
    time: Time = element(tag="Time")
    protocol: int = element(tag="Proto")
    source_port: int = element(tag="sPort")
    dest_port: int = element(tag="dPort")
    connection_begin_time: Time = element(tag="ConnectBeginTime")
    time_stamp: int = element(tag="receiveTime")
    pack_length: int = element(tag="PacketLen")
    source_ip: str = element(tag="ip_src")
    dest_ip: str = element(tag="ip_dst")

    protocol_type: ClassVar[Mapping[int, str]] = {
        1: "ICMP",
        6: "TCP",
        17: "UDP"
    }

    @override
    @classmethod
    def validate(cls, content):
        return cls.from_xml(content)

    @override
    def to_attack(self) -> AttackSchema:
        return AttackSchema(
            time=self.time,
            source_ip=self.source_ip,
            source_port=self.source_port,
            dest_ip=self.dest_ip,
            dest_port=self.dest_port,
            transport_protocol=self.protocol_type[self.protocol],
            honeypot_type=str(self.alert_type),
            attack_info="",
            source_address="",
            warning_info="",
            warning_level=0,
            content="",
        )
