from fastapi import APIRouter

from app.api.v1.controllers.subscription import ROUTER as SUBSCRIPTION_ROUTER

ROUTER = APIRouter()
ROUTER.include_router(SUBSCRIPTION_ROUTER, prefix='/sub', tags=['Client|Subscriptions'])
# Точки подключения контроллеров новой реализации:
# ROUTER.include_router(SERVER_ROUTER, prefix='/server', tags=['Client|Server'])
# ROUTER.include_router(CONFIG_ROUTER, prefix='/config', tags=['Client|Config'])
