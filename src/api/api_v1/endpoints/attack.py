import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi_injector import Injected
from websocket import WebSocketManager
from src.schema.attacks.attack import Attack

router = APIRouter()


@router.websocket("/ws")
async def send_attack_info(
    websocket: WebSocket,
    websocket_manager: WebSocketManager = Injected(WebSocketManager)
):
    await websocket.accept()

    websocket_manager.subscribe(websocket)

    # 检测websocket客户端断开
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.remove(websocket)
