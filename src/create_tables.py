import asyncio
from injector import Injector, inject
from sqlalchemy.ext.asyncio import AsyncEngine
from logger import logger
from db.models.base import ModelBase
from db import DBModule
import feature  # noqa: F401


@inject
async def main(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)
        logger.info(f"tables created: {list(ModelBase.metadata.tables)}")


if __name__ == "__main__":
    injector = Injector([DBModule()])
    asyncio.run(injector.call_with_injection(main))
