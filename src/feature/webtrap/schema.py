from datetime import datetime
from typing import Literal, Annotated
from pydantic import ConfigDict, BaseModel, IPvAnyAddress, Field, AfterValidator


class AttackSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    client_address: str = Field(examples=["127.0.0.1"])
    command: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    path: str = Field(examples=["/path?para1=val1&para2=val2"])
    request_version: str = Field(examples=["HTTP/1.1"])
    headers: str = Field(examples=["Accept: application/json, text/javascript"])
    protocol_version: str = Field(examples=["HTTP/1.0"])

    @classmethod
    def from_str(cls, content):
        return cls.model_validate_json(content)
