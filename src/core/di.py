from injector import singleton, provider, Module
from core import Settings


class SettingsModule(Module):
    @singleton
    @provider
    def provide_settings(self) -> Settings:
        return Settings()
        