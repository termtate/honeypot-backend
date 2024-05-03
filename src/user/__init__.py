from fastapi import APIRouter
from .login import router

api_router = APIRouter(prefix="/user", tags=["user"])
api_router.include_router(router)
