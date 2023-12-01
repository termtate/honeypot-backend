from injector import singleton, provider, Module
from core import Settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine
from fastapi_injector import request_scope
from .session import SessionContextManager


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
    def provide_db_session_maker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            # autoflush=False,
            future=True,
        )

    @request_scope
    @provider
    def provide_db_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> SessionContextManager:
        return SessionContextManager(session_maker())
