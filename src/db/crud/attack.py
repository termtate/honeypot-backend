from .base import CRUDWithSession, CRUDBase
from schema import AttackSchema
from db.models import Attack
from injector import inject, singleton
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class Session:
    @inject
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session


@singleton
class CRUDAttack(CRUDWithSession[AttackSchema, Attack], Session):
    crud = CRUDBase(Attack)
