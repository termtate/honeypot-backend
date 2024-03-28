from fastapi import APIRouter, FastAPI, Depends

router = APIRouter()


class CRUD:
    def get_user(self):
        ...


@router.get("/")
def hello(crud: CRUD = Depends()):
    return crud.get_user()


app = FastAPI()
app.include_router(router)
