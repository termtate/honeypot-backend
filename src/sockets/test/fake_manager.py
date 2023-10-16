from asyncio import open_connection, Queue, create_task
from typing import Any, Literal, Protocol
from schema import Attack
from asyncio import Queue
import asyncio
from datetime import datetime

def _generate_fake_attack():
    return Attack(
        time=datetime.now(),
        source_ip="0.0.0.0",
        source_port="00000",
        dest_ip="1.1.1.1",
        dest_port="11111",
        transport_protocol="ssh",
        honeypot_type="ssh",
        attack_info="attack info",
        source_address="source address",
        warning_info="warning info",
        warning_level=0,
        content="content"
    )


class FakeSocketsManager:
    def __init__(self) -> None:
        self.message_queue: Queue[Attack] = Queue(maxsize=10)
    
    
    async def _send_fake_data_forever(self, interval: int):
        while True:
            await asyncio.sleep(interval)
            await self.message_queue.put(_generate_fake_attack())
    
    
    async def open_connections(self) -> None: 
        await asyncio.gather(
            self._send_fake_data_forever(5),
            self._send_fake_data_forever(9)
        )
        
    async def get_attack_info(self) -> Attack: 
        return await self.message_queue.get()