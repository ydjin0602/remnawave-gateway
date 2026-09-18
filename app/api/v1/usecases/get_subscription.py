from httpx import AsyncClient
from loguru import logger
from remnawave import RemnawaveSDK
from remnawave.exceptions import NotFoundError as RemnawaveNotFoundError
from starlette.responses import PlainTextResponse

from app.api.utils.exceptions import NotFoundError
from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import GetSubscriptionSchema

# Заголовки, которые прокидываем от subscription-page клиенту без изменений.
PASSTHROUGH_HEADERS = (
    'content-type',
    'content-disposition',
    'subscription-userinfo',
    'profile-title',
    'profile-update-interval',
    'profile-web-page-url',
)

# Кэшируем ответ на клиенте: shortUuid юзера стабилен, лишниеlookup в ремну не нужны.
CACHE_CONTROL = 'private, max-age=300'


class GetSubscriptionUsecase(Usecase[GetSubscriptionSchema, PlainTextResponse]):
    def __init__(self, remnawave: RemnawaveSDK, http: AsyncClient) -> None:
        self._remnawave = remnawave
        self._http = http

    async def __call__(self, data: GetSubscriptionSchema) -> PlainTextResponse:
        """Отдает содержимое подписки (b64/json/clash по UA клиента)."""
        try:
            user = await self._remnawave.users.get_user_by_uuid(
                str(data.subscription_id),
            )
        except RemnawaveNotFoundError as e:
            raise NotFoundError(message='Подписка не найдена!') from e

        upstream = await self._http.get(
            user.subscription_url,
            headers={'User-Agent': data.user_agent},
        )
        upstream.raise_for_status()

        headers = {
            key: upstream.headers[key]
            for key in PASSTHROUGH_HEADERS
            if key in upstream.headers
        }
        headers['Cache-Control'] = CACHE_CONTROL

        logger.debug('Subscription proxied for {}', data.subscription_id)
        return PlainTextResponse(content=upstream.text, headers=headers)
