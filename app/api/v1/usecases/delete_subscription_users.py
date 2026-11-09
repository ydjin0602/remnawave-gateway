"""DELETE /sub/: полное удаление юзеров подписок из remnawave."""

from uuid import UUID

from loguru import logger
from remnawave import RemnawaveSDK
from remnawave.exceptions import NotFoundError as RemnawaveNotFoundError

from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import DeleteSubscriptionsSchema


class DeleteSubscriptionUsersUsecase(Usecase[DeleteSubscriptionsSchema, None]):
    """Удаление юзеров целиком: мёртвая идентичность не остаётся в панели."""

    def __init__(self, remnawave: RemnawaveSDK) -> None:
        self._remnawave = remnawave

    async def __call__(self, data: DeleteSubscriptionsSchema) -> None:
        """Метод для удаления юзеров по идентификаторам подписок."""
        for subscription_id in data.subscription_ids:
            await self._delete_user(subscription_id=subscription_id)

    async def _delete_user(self, subscription_id: UUID) -> None:
        """Ищет юзера по short_uuid и удаляет целиком.

        Идемпотентно: несуществующий id — ок, просто пропускаем.
        """
        try:
            user = await self._remnawave.users.get_user_by_short_uuid(
                short_uuid=str(subscription_id),
            )
        except RemnawaveNotFoundError:
            logger.debug('Delete: subscription {} not found, skip', subscription_id)
            return

        await self._remnawave.users.delete_user(user_id=user.id)
        logger.debug('User {} (sub {}) deleted', user.username, subscription_id)
