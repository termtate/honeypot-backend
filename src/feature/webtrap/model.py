from typing import Literal
from db.models import Base
from sqlalchemy.orm import Mapped
from datetime import datetime


class AttackOrm(Base):
    __tablename__ = "webtrap"

    client_address: Mapped[str]
    command: Mapped[Literal["GET", "POST", "PUT", "DELETE", "PATCH"]]
    path: Mapped[str]
    request_version: Mapped[str]
    headers: Mapped[str]
    protocol_version: Mapped[str]
