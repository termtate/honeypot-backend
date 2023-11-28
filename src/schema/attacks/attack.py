from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AttackSchema(BaseModel):
    """
    单次攻击的信息
    """
    time: datetime
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    transport_protocol: str
    honeypot_type: str
    attack_info: str
    source_address: str
    warning_info: str
    warning_level: int
    content: str

    model_config = ConfigDict(from_attributes=True)
