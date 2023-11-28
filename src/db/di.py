from injector import singleton, provider, Module
from core import Settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine
from .crud.generate import generate_crud
from db.models import Attack
from schema import AttackSchema
from db.crud import CRUDAttack


class DBModule(Module):
    @singleton
    @provider
    def provide_db_engine(self, settings: Settings) -> AsyncEngine:
        return create_async_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            pool_pre_ping=True,
            # echo=settings.ECHO_SQL,
        )

    @singleton
    @provider
    def provide_db_session(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            # autoflush=False,
            future=True,
        )

    @singleton
    @provider
    def provide_attack_crud(
        self, session: async_sessionmaker[AsyncSession]
    ) -> CRUDAttack:
        return generate_crud(AttackSchema, Attack)(session)
