from injector import singleton, provider, Module
from sockets.manager import AttackStream, SocketsManager
from sockets.test.fake_manager import FakeSocketsManager


class TestSocketsManagerModule(Module):
    @singleton
    @provider
    def provide_sockets_manager(self) -> SocketsManager:
        return FakeSocketsManager()

    @singleton
    @provider
    def provide_attack_stream(self, sm: SocketsManager) -> AttackStream:
        return sm.get_attack_stream()