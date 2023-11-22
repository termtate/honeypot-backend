from injector import inject, singleton
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from schema import Attack as AttackSchema
from .models.attack import Attack
from typing import AsyncIterator
from logger import Logger


@singleton
class CRUDAttack:
    """
    对orm类的查询和session的一层封装，对每一次查询都新建一个session，并且进行数据验证
    """
    @inject
    def __init__(
        self,
        session: async_sessionmaker[AsyncSession],
        logger: Logger,
    ) -> None:
        self.async_session = session
        self.logger = logger

    async def create(self, attack: AttackSchema) -> AttackSchema:
        async with self.async_session.begin() as session:
            a = await Attack.create(session, attack)
            self.logger.info(f"store attack {a} into database")
            return AttackSchema.model_validate(a, from_attributes=True)

    async def get(self, offset: int,
                  limit: int) -> AsyncIterator[AttackSchema]:
        async with self.async_session.begin() as session:
            async for attack in Attack.get(session, offset, limit):
                yield AttackSchema.model_validate(attack, from_attributes=True)
