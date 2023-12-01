from pydantic import BaseModel


class Socket(BaseModel):
    ip: str
    port: str | int
