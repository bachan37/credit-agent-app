from fastapi import APIRouter
from credit_agent_app.api.routers.credit_infos import router as credit_info_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(credit_info_router)

__all__ = [
    "api_v1_router",
    "credit_info_router",
]

