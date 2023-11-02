from injector import Injector
from main import make_app
from sockets.test import TestSocketsManagerModule


injector = Injector([TestSocketsManagerModule()])
app = make_app(injector)


if __name__ == '__main__':
    import uvicorn
    
    uvicorn.run(app, port=8000)