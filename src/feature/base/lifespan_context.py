from typing import Protocol
from contextlib import AbstractAsyncContextManager


class LifespanContext(Protocol):
    lifespan_events: set[AbstractAsyncContextManager]
