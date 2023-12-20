from datetime import datetime
from typing import Literal
from pydantic import ConfigDict, BaseModel, IPvAnyAddress


class AttackSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time: datetime
    protocol: Literal["ICMP", "TCP", "UDP"]
    source_port: int | None
    dest_port: int | None
    source_ip: IPvAnyAddress
    dest_ip: IPvAnyAddress
    content: str

    @classmethod
    def from_str(cls, content):
        return cls.model_validate_json(content)
