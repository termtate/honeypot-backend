from __future__ import annotations
from injector import Injector
from typing import Protocol, runtime_checkable, TypeVar, Type
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..honeypot import Honeypot

T = TypeVar("T", bound="Mixin")


@runtime_checkable
class Mixin(Protocol):
    @classmethod
    def configure(cls, honeypot: Type[Honeypot], injector: Injector):
        ...
