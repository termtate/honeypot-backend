from .honeyd.endpoint import router as honeyd_router
from .conpot.endpoint import router as conpot_router
from .kippo.endpoint import router as kippo_router
from .real_honeypot.endpoint import router as real_honeypot_router
from .webtrap.endpoint import router as webtrap_router
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
api_router.include_router(
    real_honeypot_router,
    prefix="/real_honeypot_attacks",
    tags=["real_honeypot"]
)
api_router.include_router(
    webtrap_router, prefix="/webtrap_attacks", tags=["webtrap"]
)
