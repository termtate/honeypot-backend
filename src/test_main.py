from injector import Injector
from main import make_app

if __name__ == '__main__':
    import uvicorn

    injector = Injector()
    
    uvicorn.run(make_app(injector), port=8000)