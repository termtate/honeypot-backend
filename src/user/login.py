from pydantic import BaseModel
from fastapi import APIRouter


class UserLogin(BaseModel):
    username: str
    password: str


class UserLoginResponse(UserLogin):
    role: str
    roleId: str
    permissions: list[str]


router = APIRouter()


@router.post("/login")
async def login(form: UserLogin) -> UserLoginResponse:
    return UserLoginResponse(
        username=form.username,
        password=form.password,
        role="1",
        roleId="1",
        permissions=["2"],
    )
