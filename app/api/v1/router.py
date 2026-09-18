from fastapi import APIRouter

from app.api.v1.controllers.router import ROUTER as CONTROLLERS_ROUTER

ROUTER = APIRouter()

ROUTER.include_router(CONTROLLERS_ROUTER)
