from fastapi import APIRouter
from api.api_v1.endpoints import attack 

api_router = APIRouter()
api_router.include_router(attack.router, prefix="/attack", tags=["attack"])

