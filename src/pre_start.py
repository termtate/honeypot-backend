import asyncio
from injector import Injector, inject
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select
from db import DBModule
from logger import logger


@inject
async def main(engine: AsyncEngine):
    logger.debug("start connecting database")
    async with engine.begin() as conn:
        logger.debug("database connected")
        await conn.execute(select(1))
        logger.debug("statement executed")
    logger.debug("database disconnected")


if __name__ == "__main__":
    injector = Injector([DBModule()])
    asyncio.run(injector.call_with_injection(main))
