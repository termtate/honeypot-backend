from injector import singleton, provider, Module
from core import setting
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_injector import request_scope
from .session import SessionContextManager


class DBModule(Module):
    @singleton
    @provider
    def provide_db_engine(self) -> AsyncEngine:
        return create_async_engine(
            str(setting.SQLALCHEMY_DATABASE_URI),
            future=True,
            # echo=settings.ECHO_SQL,
        )

    @singleton
    @provider
    def provide_db_session_maker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            autocommit=False,
            bind=engine,
            autoflush=False,
            future=True,
            class_=AsyncSession,
        )

    @request_scope
    @provider
    def provide_db_session_context_manager(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> SessionContextManager:
        return SessionContextManager(session_maker())

    @provider
    def provide_db_session(
        self, context: SessionContextManager
    ) -> AsyncSession:
        return context.async_session
