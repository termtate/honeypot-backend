from injector import singleton, provider, Module
from sockets.manager import RealSocketsManager, SocketsManager
from sockets.test.fake_manager import FakeSocketsManager
from core import Settings


class TestSocketsManagerModule(Module):
    @singleton
    @provider
    def provide_sockets_manager(self) -> SocketsManager:
        return FakeSocketsManager()