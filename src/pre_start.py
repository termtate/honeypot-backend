import asyncio
from injector import Injector, inject
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select
from logger import Logger
from db.models import Attack
from db import DBModule
from logger import LoggerModule


@inject
async def main(engine: AsyncEngine, logger: Logger):
    logger.debug("start connecting database")
    async with engine.begin() as conn:
        logger.debug("database connected")
        await conn.execute(select(Attack))
        logger.debug("statement executed")
    logger.debug("database disconnected")


if __name__ == "__main__":
    injector = Injector([DBModule(), LoggerModule()])
    asyncio.run(injector.call_with_injection(main))
