from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class Attack(BaseModel):
    """
    单次攻击的信息
    """
    time: datetime
    source_ip: str
    source_port: str | int
    dest_ip: str
    dest_port: str | int
    transport_protocol: str
    honeypot_type: str
    attack_info: str
    source_address: str
    warning_info: str
    warning_level: int
    content: str