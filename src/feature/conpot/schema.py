from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AttackSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request: str
    slave_id: int
    function_code: int
    response: str
    time: datetime
    session_id: str

    @classmethod
    def from_str(cls, content):
        return cls.model_validate_json(content)
