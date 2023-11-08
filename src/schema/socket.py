from schema.attacks.alt import AttackValidator
from pydantic import BaseModel
from typing import TypeVar, Generic, Type, Callable
from schema import Attack


class Socket(BaseModel):
    ip: str
    port: str | int
    attack_validator: Type[AttackValidator]
    
