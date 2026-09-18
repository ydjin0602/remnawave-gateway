from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import GetSubscriptionSchema
from app.api.v1.schemas.subscription import SubscriptionSchema


class DisableAutoRenewUsecase(Usecase[GetSubscriptionSchema, SubscriptionSchema]):
    """Usecase отключения автоматического продления подписки."""

    async def __call__(self, data: GetSubscriptionSchema) -> SubscriptionSchema:
        """Переключает флаг автопродления на false."""
        # TODO: Новая реализация на Remnawave API.
        #  Старый флоу (git-история vpn-subscriptions): переключить флаг
        #  auto_renew у подписки и вернуть обновленную SubscriptionSchema.
        raise NotImplementedError
