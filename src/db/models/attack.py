from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, MappedAsDataclass
import pydantic
from datetime import datetime
from sqlalchemy import select
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self
from schema import Attack as AttackSchema
from pydantic import ConfigDict

# 使用 sqlalchemy 的声明式orm类创建sql表和查询方法


class Base(
        MappedAsDataclass,  # 可转换为dataclass
        DeclarativeBase,  # sqlalchemy orm 声明式基类
        dataclass_callable=pydantic.dataclasses.dataclass(config=ConfigDict(
            from_attributes=True)),  # 与pydantic集成
):
    pass


class Attack(Base):
    __tablename__ = "attacks"

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        unique=True,
        primary_key=True,
        init=
        False,  # https://stackoverflow.com/questions/77452233/instantiated-a-sqlalchemy-declarative-mapped-class-requires-the-autogenerated-an
    )

    time: Mapped[datetime]
    source_ip: Mapped[str]
    source_port: Mapped[int]
    dest_ip: Mapped[str]
    dest_port: Mapped[int]
    transport_protocol: Mapped[str]
    honeypot_type: Mapped[str]
    attack_info: Mapped[str]
    source_address: Mapped[str]
    warning_info: Mapped[str]
    warning_level: Mapped[int]
    content: Mapped[str]

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        offset: int | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Self]:
        stmt = select(cls).order_by(cls.id).offset(offset).limit(limit)
        stream = await session.stream_scalars(stmt)
        async for row in stream:
            yield row

    @classmethod
    async def get_by_id(
        cls, session: AsyncSession, attack_id: int
    ) -> Self | None:
        stmt = select(cls).where(cls.id == attack_id)
        return await session.scalar(stmt)

    @classmethod
    async def create(cls, session: AsyncSession, attack: AttackSchema) -> Self:
        a = cls(**attack.model_dump())
        session.add(a)
        await session.flush()
        new = await cls.get_by_id(session, a.id)
        assert new is not None
        return new