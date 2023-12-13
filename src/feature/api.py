from .honeyd.endpoint import router as honeyd_router
from .conpot.endpoint import router as conpot_router
from .kippo.endpoint import router as kippo_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(
    honeyd_router, prefix="/honeyd_attacks", tags=["honeyd"]
)
api_router.include_router(
    conpot_router, prefix="/conpot_attacks", tags=["conpot"]
)
api_router.include_router(
    kippo_router, prefix="/kippo_attacks", tags=["kippo"]
)
