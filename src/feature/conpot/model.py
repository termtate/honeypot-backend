from db.models import Base
from sqlalchemy.orm import Mapped
from datetime import datetime


class AttackOrm(Base):
    __tablename__ = "conpot"

    request: Mapped[str]
    slave_id: Mapped[int]
    function_code: Mapped[int]
    response: Mapped[str]
    time: Mapped[datetime]
    session_id: Mapped[str]