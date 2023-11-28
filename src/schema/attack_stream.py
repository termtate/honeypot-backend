from typing import TypeAlias
from .attacks.attack import AttackSchema
from aioreactive import AsyncObservable

AttackStream: TypeAlias = AsyncObservable[AttackSchema]
