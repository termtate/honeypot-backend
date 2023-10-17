import asyncio
from fastapi import WebSocket
from sockets import SocketsManager
from injector import inject


class WebSocketManager:
    @inject
    def __init__(self, sockets_manager: SocketsManager) -> None:
        self.websocket_connections: list[WebSocket] = []
        self.sockets_manager = sockets_manager
        
        self._running_tasks: asyncio.Task | None = None
    
    
    async def _start_listening_sockets(self):    
        while True:
            attack = await self.sockets_manager.get_attack_info()
            await asyncio.gather(*[
                websocket.send_text(attack.model_dump_json()) for websocket in self.websocket_connections
            ])
    
    
    def subscribe(self, websocket: WebSocket):
        if len(self.websocket_connections) == 0:
            assert self._running_tasks is None
            self._running_tasks = asyncio.create_task(self._start_listening_sockets())
            
        self.websocket_connections.append(websocket)
    
    
    def remove(self, websocket: WebSocket):
        assert self._running_tasks is not None
        
        self.websocket_connections.remove(websocket)
        
        if len(self.websocket_connections) == 0:
            self._running_tasks.cancel()
            self._running_tasks = None
    
    
    
