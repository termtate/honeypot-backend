import contextlib
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi_injector import Injected
from .crud import CRUDAttack
from .websocket import ConpotWebsocket
from .schema import AttackSchema
from .source import ConpotSource

router = APIRouter()


@router.websocket("/ws")
async def send_attack_info(
    websocket: WebSocket,
    subscribe: ConpotWebsocket = Injected(ConpotWebsocket)
):
    await websocket.accept()

    with subscribe(websocket):
        with contextlib.suppress(WebSocketDisconnect):
            while True:
                await websocket.receive_text()


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
    source: ConpotSource = Injected(ConpotSource),
    crud: CRUDAttack = Injected(CRUDAttack),
):
    new = await crud.create(attack)
    await source.stream.asend(attack)
    return new