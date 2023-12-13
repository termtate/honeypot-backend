from db.models import Base
from sqlalchemy.orm import Mapped
from datetime import datetime


class AttackOrm(Base):
    __tablename__ = "kippo"

    content: Mapped[str]
    time: Mapped[datetime]
