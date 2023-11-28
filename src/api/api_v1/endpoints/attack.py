from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi_injector import Injected
from websocket import WebSocketManager
from schema import AttackSchema as AttackSchema
from db.models import Attack
from db import CRUDAttack

router = APIRouter()


@router.websocket("/ws")
async def send_attack_info(
    websocket: WebSocket,
    websocket_manager: WebSocketManager = Injected(WebSocketManager),
):
    await websocket.accept()

    websocket_manager.subscribe(websocket)

    # 检测websocket客户端断开
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.remove(websocket)


@router.get("/", response_model=list[AttackSchema])
async def get_attacks(
    offset: int = 0,
    limit: int = 10,
    crud: CRUDAttack = Injected(CRUDAttack)
) -> list[Attack]:

    return [attack async for attack in await crud.get(offset, limit)]
