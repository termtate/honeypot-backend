from typing import Literal
from db.models import Base
from sqlalchemy.orm import Mapped
from datetime import datetime


class AttackOrm(Base):
    __tablename__ = "real_honeypot"

    time: Mapped[datetime]
    protocol: Mapped[Literal["ICMP", "TCP", "UDP"]]
    source_port: Mapped[int | None]
    dest_port: Mapped[int | None]
    source_ip: Mapped[str]
    dest_ip: Mapped[str]
    content: Mapped[str]
