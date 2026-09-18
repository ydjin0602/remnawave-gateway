from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi import Depends
from starlette.responses import HTMLResponse

from app.api.utils.security import authenticate_swagger
from app.api.utils.swagger.ui import get_swagger_ui_html

ROUTER = APIRouter(
    route_class=DishkaRoute,
)


@ROUTER.get(
    '/docs',
    include_in_schema=False,
    dependencies=[Depends(authenticate_swagger)],
)
async def custom_swagger_ui_html() -> HTMLResponse:
    """Генерация кастомного html для сваггера."""
    return get_swagger_ui_html(
        openapi_url='/openapi.json',
        swagger_ui_parameters={
            'defaultModelsExpandDepth': -1,  # убирает раздел со схемами внизу
            'displayRequestDuration': True,
        },
    )
