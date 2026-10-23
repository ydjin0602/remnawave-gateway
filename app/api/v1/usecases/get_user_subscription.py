from remnawave import RemnawaveSDK
from remnawave.exceptions import NotFoundError as RemnawaveNotFoundError

from app.api.utils.exceptions import NotFoundError
from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import GetUserSubscriptionSchema
from app.api.v1.schemas.subscription import SubscriptionSchema
from app.api.v1.usecases.subscribe import user_to_subscription_schema


class GetUserSubscriptionUsecase(
    Usecase[GetUserSubscriptionSchema, SubscriptionSchema]
):
    def __init__(self, remnawave: RemnawaveSDK) -> None:
        self._remnawave = remnawave

    async def __call__(self, data: GetUserSubscriptionSchema) -> SubscriptionSchema:
        """Метаданные подписки по tg-id (username ремны = str(tg-id))."""
        try:
            user = await self._remnawave.users.get_user_by_username(
                username=str(data.user_id),
            )
        except RemnawaveNotFoundError as e:
            raise NotFoundError(message='Подписка не найдена!') from e
        return user_to_subscription_schema(user)
