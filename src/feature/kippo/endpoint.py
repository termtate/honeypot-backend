from fastapi import APIRouter
from fastapi_injector import Injected
from .crud import CRUDAttack

router = APIRouter()


@router.get("/")
async def get_attacks(
    offset: int = 0,
    limit: int = 10,
    crud: CRUDAttack = Injected(CRUDAttack),
):
    return [attack async for attack in crud.get(offset, limit)]
