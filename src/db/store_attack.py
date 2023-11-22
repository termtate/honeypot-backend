from injector import inject
from .crud import CRUDAttack
from aioreactive import AsyncIteratorObserver
from sockets import SocketsManager


@inject
async def store_attacks_to_db(
    crud_attack: CRUDAttack, sockets_manager: SocketsManager
):
    async for attack in AsyncIteratorObserver(
            sockets_manager.get_attack_stream()):
        await crud_attack.create(attack)
