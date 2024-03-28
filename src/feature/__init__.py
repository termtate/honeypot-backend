from typing import Type
from .base import Honeypot
from .utils.lifespan_scope import (
    LifespanScope as LifespanScope,
    lifespan_scope as lifespan_scope,
)
from fastapi import APIRouter
from .conpot import Conpot
from .honeyd import Honeyd
from .kippo import Kippo
from .real_honeypot import RealHoneypot
from .webtrap import Webtrap

all_honeypots: list[Type[Honeypot]] = [
    Conpot,
    Honeyd,
    Kippo,
    RealHoneypot,
    Webtrap,
]

for honeypot in all_honeypots:
    honeypot.configure()

honeypot_binds = [honeypot.bind_class_types for honeypot in all_honeypots]

honeypot_routers = [honeypot.router for honeypot in all_honeypots]

api_router = APIRouter()
for router in honeypot_routers:
    api_router.include_router(router)
