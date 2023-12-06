from .honeyd.endpoint import router as honeyd_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(honeyd_router, prefix="/attacks", tags=["attack"])
