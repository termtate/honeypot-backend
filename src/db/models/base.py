from sqlmodel import SQLModel, Field
from datetime import datetime


class ModelBase(SQLModel):
    """
    数据库 orm基类
    """

    id: int | None = Field(default=None, primary_key=True, unique=True)
    time: datetime = Field(default_factory=datetime.now)
