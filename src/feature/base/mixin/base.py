from __future__ import annotations

from typing import Protocol, runtime_checkable, TypeVar, Type


T = TypeVar("T", bound="Mixin")


@runtime_checkable
class Mixin(Protocol):
    @classmethod
    def configure_mixin(cls, honeypot: Type[T]):
        ...
