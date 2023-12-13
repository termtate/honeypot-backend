from ..utils import store_attack, lifespan_scope
from injector import Injector
from .source import KippoSource
from .crud import CRUDAttack


@lifespan_scope.on_startup
def store_attacks_to_db(injector: Injector):
    return store_attack(KippoSource, CRUDAttack)(injector)