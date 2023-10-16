from injector import Injector
from core import SettingsModule
from sockets.test import TestSocketsManagerModule
from main import make_app

if __name__ == '__main__':
    import uvicorn

    injector = Injector([TestSocketsManagerModule(), SettingsModule()])
    
    uvicorn.run(make_app(injector), port=8000)