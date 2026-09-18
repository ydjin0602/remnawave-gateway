from starlette.responses import PlainTextResponse

from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import GetSubscriptionSchema


class GetSubscriptionUsecase(Usecase[GetSubscriptionSchema, PlainTextResponse]):
    """Usecase получения подписки для vpn клиентов."""

    async def __call__(self, data: GetSubscriptionSchema) -> PlainTextResponse:
        """Отдает ключи, каждый на своей строке, в b64."""
        # TODO: Новая реализация на Remnawave API.
        #  Старый флоу (git-история, app/api/v1/usecases/get_subscription.py):
        #  1. проверить кэш по subscription_id, при попадании - вернуть
        #  2. загрузить подписку с конфигами (get_subscription_with_configs)
        #  3. фильтр конфигов: grace-период -> только free-группа,
        #     иначе - только платные
        #  4. собрать vless-строки с каждого сервера (_fetch_config_line,
        #     ошибки сервера -> пропустить строку)
        #  5. собрать xray-профиль автовыбора + закодировать в b64
        #  6. сформировать заголовки sub-info (upload/download/total/expire,
        #     для INCY - с цветом и announce-текстом)
        #  7. закэшировать ответ и вернуть PlainTextResponse
        raise NotImplementedError
