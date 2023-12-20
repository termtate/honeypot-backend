from fastapi import APIRouter
from fastapi_injector import Injected
from .crud import CRUDAttack
from .schema import AttackSchema
from .source import RealHoneypotSource
from logger import Logger

router = APIRouter()


@router.get("/")
async def get_attacks(
    offset: int = 0,
    limit: int = 10,
    crud: CRUDAttack = Injected(CRUDAttack),
):
    return [attack async for attack in crud.get(offset, limit)]


@router.post("/")
async def create_attack(
    attack: AttackSchema,
    source: RealHoneypotSource = Injected(RealHoneypotSource),
    crud: CRUDAttack = Injected(CRUDAttack),
    logger: Logger = Injected(Logger)
):
    new = await crud.create(attack)
    logger.info(f"created attack {new}")
    await source.stream.asend(attack)
    return new
