from injector import Binder, singleton, provider, Module
from sockets.manager import RealSocketsManager, SocketsManager
from core import Settings
from schema import Socket
from logger import Logger


class SocketsManagerModule(Module):

    @singleton
    @provider
    def provide_sockets_manager(
        self, settings: Settings, logger: Logger
    ) -> SocketsManager:
        return RealSocketsManager(settings.sockets, logger)