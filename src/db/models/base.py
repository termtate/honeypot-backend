from typing_extensions import Self
from sqlmodel import SQLModel


class Base(SQLModel):
    """
    数据库 orm基类
    """
    @classmethod
    def from_str(cls, content: str | bytes) -> Self:
        return cls.model_validate_json(content)
