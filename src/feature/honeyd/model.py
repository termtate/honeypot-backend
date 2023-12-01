from db.models import Base
from sqlalchemy.orm import Mapped
from datetime import datetime


class AttackOrm(Base):
    __tablename__ = "attacks"

    symbol: Mapped[int]
    alert_type: Mapped[int]
    subtype: Mapped[int]
    time: Mapped[datetime]
    protocol: Mapped[str]
    source_port: Mapped[int]
    dest_port: Mapped[int]
    connection_begin_time: Mapped[datetime]
    time_stamp: Mapped[int]
    pack_length: Mapped[int]
    source_ip: Mapped[str]
    dest_ip: Mapped[str]
