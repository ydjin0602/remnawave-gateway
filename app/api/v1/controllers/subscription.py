from uuid import UUID

from dishka import FromDishka as Depends
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi import Depends as FastAPIDepends
from starlette.responses import PlainTextResponse
from starlette.responses import RedirectResponse
from starlette.status import HTTP_204_NO_CONTENT

from app.api.utils.enums.app_enum import AppEnum
from app.api.utils.security import authenticate_by_api_key
from app.api.v1.schemas.subscription import CreateSubscriptionSchema
from app.api.v1.schemas.subscription import GetSubscriptionSchema
from app.api.v1.schemas.subscription import RevokeSubscriptionsSchema
from app.api.v1.schemas.subscription import SubscriptionSchema
from app.api.v1.usecases.get_subscription import GetSubscriptionUsecase
from app.api.v1.usecases.incy_redirect import IncyRedirectUsecase
from app.api.v1.usecases.revoke_subscription import RevokeSubscriptionUsecase
from app.api.v1.usecases.subscribe import SubscribeUsecase

ROUTER = APIRouter(
    route_class=DishkaRoute,
)


@ROUTER.post(
    '/',
    name='Ручка для создания и продления подписки',
    description='При продлении подписка сразу принимает последнюю конфигурацию',
    response_model=SubscriptionSchema,
    dependencies=[FastAPIDepends(authenticate_by_api_key)],
)
async def subscribe(
    payload: CreateSubscriptionSchema,
    usecase: Depends[SubscribeUsecase],
) -> SubscriptionSchema:
    return await usecase(data=payload)


@ROUTER.get(
    '/{subscription_id}/incy_redirect',
    name='Ручка для редиректа на incy',
    description='Редиректит на диплинк incy',
    response_class=RedirectResponse,
)
async def incy_redirect(
    subscription_id: UUID,
    usecase: Depends[IncyRedirectUsecase],
) -> RedirectResponse:
    return await usecase(
        data=GetSubscriptionSchema(
            subscription_id=subscription_id,
        ),
    )


@ROUTER.get(
    '/{subscription_id}/incy',
    name='Ручка для получения подписки из vpn клиентов для incy',
    description='Тут перечислены ключи, каждый на своей строке, в b64 для incy',
    response_class=PlainTextResponse,
)
async def get_incy_subscription(
    subscription_id: UUID,
    usecase: Depends[GetSubscriptionUsecase],
) -> PlainTextResponse:
    return await usecase(
        data=GetSubscriptionSchema(
            subscription_id=subscription_id,
            app=AppEnum.INCY,
        ),
    )


@ROUTER.get(
    '/{subscription_id}',
    name='Ручка для получения подписки из vpn клиентов',
    description='Тут перечислены ключи, каждый на своей строке, в b64',
    response_class=PlainTextResponse,
)
async def get_subscription(
    subscription_id: UUID,
    usecase: Depends[GetSubscriptionUsecase],
) -> PlainTextResponse:
    return await usecase(
        data=GetSubscriptionSchema(
            subscription_id=subscription_id,
        ),
    )


@ROUTER.delete(
    '/',
    name='Ручка для отмены подписок',
    description='Фактически мы принудительно завершаем подписку с момента вызова '
    'ручки.',
    status_code=HTTP_204_NO_CONTENT,
)
async def revoke_subscription(
    payload: RevokeSubscriptionsSchema,
    usecase: Depends[RevokeSubscriptionUsecase],
) -> None:
    await usecase(
        data=payload,
    )
