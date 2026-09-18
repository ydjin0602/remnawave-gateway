from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import CreateSubscriptionSchema
from app.api.v1.schemas.subscription import SubscriptionSchema


class SubscribeUsecase(Usecase[CreateSubscriptionSchema, SubscriptionSchema]):
    """Usecase создания и продления подписки."""

    async def __call__(self, data: CreateSubscriptionSchema) -> SubscriptionSchema:
        """Метод для подписки на впн."""
        # TODO: Новая реализация на Remnawave API.
        #  Старый флоу (git-история, app/api/v1/usecases/subscribe.py):
        #  1. create_with_conflict(subscription) - upsert подписки
        #  2. если у подписки уже есть конфиги:
        #     - пометить их PENDING_FOR_SYNC
        #     иначе:
        #     - assign_configs_to_subscription (выдать свободные конфиги)
        #  3. инвалидировать кэш подписки
        #  4. вернуть обновленную SubscriptionSchema
        raise NotImplementedError
