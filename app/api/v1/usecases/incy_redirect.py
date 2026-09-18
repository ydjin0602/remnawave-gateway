from starlette.responses import RedirectResponse

from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import GetSubscriptionSchema
from app.config import config


class IncyRedirectUsecase(Usecase[GetSubscriptionSchema, RedirectResponse]):
    async def __call__(self, data: GetSubscriptionSchema) -> RedirectResponse:
        """Редирект на incy."""
        redirect_link = config.gateway.incy_redirect_tmp.format(
            id=data.subscription_id,
        )
        return RedirectResponse(url=redirect_link)
