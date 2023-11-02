from schema import Attack
from asyncio import Queue
import asyncio
from datetime import datetime
from injector import singleton, inject
from sockets.manager import SocketsManager
from typing_extensions import override
from random import choice
from faker import Faker
from faker.providers import internet

faker = Faker()
faker.add_provider(internet)


def _generate_fake_attack():
    return Attack(
        time=datetime.now(),
        source_ip=faker.ipv4(),
        source_port=faker.port_number(),
        dest_ip=faker.ipv4(),
        dest_port=faker.port_number(),
        transport_protocol=choice(["ssh", "modbus", "s7comm"]),
        honeypot_type=choice(["ssh", "modbus", "s7comm"]),
        attack_info=choice(["users", "port", "login"]),
        source_address="China",
        warning_info="warning info",
        warning_level=choice([0, 1, 2, 3]),
        content="content"
    )


# @singleton
class FakeSocketsManager(SocketsManager):
    def __init__(self) -> None:
        self.message_queue: Queue[Attack] = Queue(maxsize=10)
        self.tasks: list[asyncio.Task] | None = None
    
    
    async def _send_fake_data_forever(self, interval: int):
        while True:
            await asyncio.sleep(interval)
            await self.message_queue.put(_generate_fake_attack())
    
    @override
    def open_connections(self) -> None: 
        self.tasks = [
            asyncio.create_task(self._send_fake_data_forever(5)),
            asyncio.create_task(self._send_fake_data_forever(9)),
        ]
    
    @override
    async def get_attack_info(self) -> Attack: 
        return await self.message_queue.get()

    @override
    def close_connections(self) -> None:
        if self.tasks is not None:
            for task in self.tasks:
                task.cancel()