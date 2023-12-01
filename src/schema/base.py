from typing import Protocol
from typing_extensions import Self


class Schema(Protocol):
    @classmethod
    def from_str(cls, content: bytes | str) -> Self:
        ...

    def model_dump_json(self) -> str:
        ...
