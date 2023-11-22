from typing import TypeAlias
from .attacks.attack import Attack
from aioreactive import AsyncObservable

AttackStream: TypeAlias = AsyncObservable[Attack]
