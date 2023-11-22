from injector import Injector
from main import make_app
from sockets.test import TestSocketsManagerModule

injector = Injector([TestSocketsManagerModule()])
app = make_app(injector)
