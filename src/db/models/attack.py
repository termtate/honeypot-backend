from sqlalchemy.orm import Mapped
from datetime import datetime
from schema import AttackSchema as AttackSchema
from .base import Base


class Attack(Base):
    __tablename__ = "attacks"

    time: Mapped[datetime]
    source_ip: Mapped[str]
    source_port: Mapped[int]
    dest_ip: Mapped[str]
    dest_port: Mapped[int]
    transport_protocol: Mapped[str]
    honeypot_type: Mapped[str]
    attack_info: Mapped[str]
    source_address: Mapped[str]
    warning_info: Mapped[str]
    warning_level: Mapped[int]
    content: Mapped[str]
