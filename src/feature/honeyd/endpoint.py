import contextlib
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi_injector import Injected
from .crud import CRUDAttack
from .websocket import HoneydWebsocket

router = APIRouter()


@router.websocket("/ws")
async def send_attack_info(
    websocket: WebSocket,
    subscribe: HoneydWebsocket = Injected(HoneydWebsocket)
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
