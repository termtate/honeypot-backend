import asyncio
from injector import Injector, inject
from sqlalchemy.ext.asyncio import AsyncEngine
from logger import Logger
from db.models.base import ModelBase
from db import DBModule
from logger import LoggerModule
import feature  # noqa: F401


@inject
async def main(engine: AsyncEngine, logger: Logger):
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
        logger.warning("all tables dropped")


if __name__ == "__main__":
    injector = Injector([DBModule(), LoggerModule()])
    asyncio.run(injector.call_with_injection(main))
