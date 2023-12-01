from db.crud import CRUDWithSession, CRUDBase
from .model import AttackOrm
from .schema import AttackSchema
from injector import inject
from fastapi_injector import request_scope
from db import SessionContextManager


@request_scope
class CRUDAttack(CRUDWithSession[AttackSchema, AttackOrm]):
    crud = CRUDBase(AttackOrm)

    @inject
    def __init__(self, context_manager: SessionContextManager):
        self.session = context_manager.async_session