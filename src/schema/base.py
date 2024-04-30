from typing_extensions import Self
from sqlmodel import SQLModel


class Schema(SQLModel):
    @classmethod
    def from_str(cls, content: str | bytes) -> Self:
        return cls.model_validate_json(content)


# class Schema(Protocol):
#     @classmethod
#     def from_str(cls, content: bytes | str) -> Self:
#         ...

#     def model_dump_json(self) -> str:
#         ...

#     def model_dump(self) -> dict[str, Any]:
#         ...
