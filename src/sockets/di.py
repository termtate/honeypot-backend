from injector import singleton, provider, Module
from sockets.manager import RealSocketsManager, SocketsManager
from core import Settings


class SocketsManagerModule(Module):
    @singleton
    @provider
    def provide_sockets_manager(self, settings: Settings) -> SocketsManager:
        return RealSocketsManager(settings.sockets)