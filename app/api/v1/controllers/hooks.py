from dishka import FromDishka as Depends
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import ORJSONResponse

from app.api.v1.schemas.hook import RemnawaveHookSchema
from app.api.v1.usecases.remnawave_hook import RemnawaveHookUsecase

ROUTER = APIRouter(
    route_class=DishkaRoute,
)


@ROUTER.post(
    '/remnawave',
    name='Ручка приема хуков Remnawave',
    description='Хуки user.expired / user.expiration конвертируются в события '
    'для vpn-bot. Авторизация по HMAC-подписи '
    '(x-remnawave-signature / x-remnawave-timestamp).',
    response_class=ORJSONResponse,
)
async def remnawave_hook(
    request: Request,
    usecase: Depends[RemnawaveHookUsecase],
) -> ORJSONResponse:
    # HMAC считается по сырому телу — парсим тело как есть.
    body = (await request.body()).decode('utf-8')
    await usecase(
        data=RemnawaveHookSchema(
            body=body,
            headers=dict(request.headers),
        ),
    )
    return ORJSONResponse(content={})
