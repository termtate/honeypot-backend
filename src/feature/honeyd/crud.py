from db.crud import CRUDWithSession, CRUDBase
from .model import AttackOrm
from .schema import AttackSchema
from fastapi_injector import request_scope
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils import inject_constructor


@request_scope
@inject_constructor
class CRUDAttack(CRUDWithSession[AttackSchema, AttackOrm]):
    crud = CRUDBase(AttackOrm)
    session: AsyncSession
