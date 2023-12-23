from datetime import datetime
from typing import Literal, Annotated
from pydantic import ConfigDict, BaseModel, IPvAnyAddress, AfterValidator


class AttackSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time: datetime
    protocol: Literal["ICMP", "TCP", "UDP"]
    source_port: int | None
    dest_port: int | None
    source_ip: str
    dest_ip: str
    content: str

    @classmethod
    def from_str(cls, content):
        return cls.model_validate_json(content)
