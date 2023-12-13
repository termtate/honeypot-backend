from fastapi import APIRouter
from fastapi_injector import Injected
from .crud import CRUDAttack
from .schema import AttackSchema
from .source import KippoSource

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
    source: KippoSource = Injected(KippoSource),
    crud: CRUDAttack = Injected(CRUDAttack),
):
    new = await crud.create(attack)
    await source.stream.asend(attack)
    return new
