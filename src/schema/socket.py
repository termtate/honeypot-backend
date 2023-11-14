from schema.attacks.alt import AttackValidator
from pydantic import BaseModel
from typing import Type


class Socket(BaseModel):
    ip: str
    port: str | int
    attack_validator: Type[AttackValidator]
