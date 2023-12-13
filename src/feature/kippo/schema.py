from datetime import datetime
from pydantic import ConfigDict, BaseModel, Field


class AttackSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    time: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_str(cls, content):
        return cls(content=content)
