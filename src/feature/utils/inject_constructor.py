from typing import TypeVar, Type
from typing_extensions import dataclass_transform
import dataclasses
from injector import inject

T = TypeVar("T")


@dataclass_transform()
def inject_constructor(cls: Type[T]) -> Type[T]:
    """
    装饰一个类，让这个类：
    1. 能像`dataclasses.dataclass`一样声明构造参数
    2. `__init__`方法被`injector.inject`装饰
    """
    new = dataclasses.dataclass(repr=False, eq=False)(cls)
    return inject(new)
