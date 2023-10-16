import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi_injector import Injected
from sockets.manager import SocketsManager
from schema.attack import Attack

router = APIRouter()


@router.websocket("/ws")
async def send_attack_info(
    websocket: WebSocket, 
    sockets_manager: SocketsManager = Injected(SocketsManager)
):
    await websocket.accept()
    async def send():
         while True:
            attack = await sockets_manager.get_attack_info()
            await websocket.send_text(attack.model_dump_json())
    task = asyncio.create_task(send())
    
    # 检测websocket客户端断开
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        task.cancel()
