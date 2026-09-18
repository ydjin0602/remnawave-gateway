from starlette.responses import RedirectResponse

from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import GetSubscriptionSchema


class IncyRedirectUsecase(Usecase[GetSubscriptionSchema, RedirectResponse]):
    """Usecase редиректа на incy."""

    async def __call__(self, data: GetSubscriptionSchema) -> RedirectResponse:
        """Редирект на incy."""
        # TODO: Новая реализация.
        #  Старый флоу (git-история, app/api/v1/usecases/incy_redirect.py):
        #  RedirectResponse(url=f'incy://import/{base_url}/api/v1/sub/{id}')
        raise NotImplementedError
