from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import RevokeSubscriptionsSchema


class RevokeSubscriptionUsecase(Usecase[RevokeSubscriptionsSchema, None]):
    """Usecase принудительного завершения подписок."""

    async def __call__(self, data: RevokeSubscriptionsSchema) -> None:
        """Фактически мы принудительно завершаем подписку с момента вызова."""
        # TODO: Новая реализация на Remnawave API.
        #  Старый флоу (git-история, app/api/v1/usecases/revoke_subscription.py):
        #  1. батчами по batch_limit:
        #     - пометить подписки истекшими (set_many_expired)
        #     - собрать конфиги на отзыв по серверам (get_configs_to_revoke)
        #  2. по каждому серверу через XUI-клиент удалить клиентов
        #     (DeleteClientsSchema), ошибки - логировать, не ронять батч
        #  3. проставить статус SYNCED отозванным конфигам
        #  4. инвалидировать кэш подписок
        raise NotImplementedError
