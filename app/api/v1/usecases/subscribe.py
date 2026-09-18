from loguru import logger
from remnawave import RemnawaveSDK
from remnawave.exceptions import ConflictError
from remnawave.exceptions import NotFoundError
from remnawave.models.users import CreateUserRequestDto
from remnawave.models.users import CreateUserResponseDto
from remnawave.models.users import GetUserByUsernameResponseDto
from remnawave.models.users import UpdateUserRequestDto
from remnawave.models.users import UpdateUserResponseDto

from app.api.utils.usecase import Usecase
from app.api.v1.schemas.subscription import CreateSubscriptionSchema
from app.api.v1.schemas.subscription import SubscriptionSchema

GIGABYTE = 2**30


type TUserResponse = (
    CreateUserResponseDto | UpdateUserResponseDto | GetUserByUsernameResponseDto
)


class SubscribeUsecase(Usecase[CreateSubscriptionSchema, SubscriptionSchema]):
    """Usecase создания и продления подписки (create-or-renew)."""

    def __init__(self, remnawave: RemnawaveSDK) -> None:
        self._remnawave = remnawave

    async def __call__(self, data: CreateSubscriptionSchema) -> SubscriptionSchema:
        """Метод для подписки на впн."""
        user = await self._upsert_user(data)
        return self._to_response(user)

    def _to_response(self, user: TUserResponse) -> SubscriptionSchema:
        """Собирает ответ старого контракта из DTO ремны.

        effective_expires_at = expire_at (стратегия NO_RESET).
        """
        return SubscriptionSchema(
            id=user.uuid,
            user_id=user.username,
            traffic_limit=user.traffic_limit_bytes // GIGABYTE,
            connections_limit=user.hwid_device_limit or 0,
            expires_at=user.expire_at,
            effective_expires_at=user.expire_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def _upsert_user(self, data: CreateSubscriptionSchema) -> TUserResponse:
        """Создает юзера ремны или продлевает существующего."""
        username = str(data.user_id)
        mutable_fields = {
            'expire_at': data.expires_at,
            'traffic_limit_bytes': data.traffic_limit * GIGABYTE,
            'hwid_device_limit': data.connections_limit,
            'telegram_id': data.user_id,
        }

        existing = await self._find_user(username)

        if existing:
            updated = await self._remnawave.users.update_user(
                UpdateUserRequestDto(
                    uuid=existing.uuid,
                    username=username,
                    **mutable_fields,
                ),
            )
            logger.debug('Subscription renewed for {}', username)
            return updated

        try:
            created = await self._remnawave.users.create_user(
                CreateUserRequestDto(
                    username=username,
                    **mutable_fields,
                ),
            )
        except ConflictError:
            # Гонка: юзер создан параллельным запросом — продлеваем его.
            existing = await self._find_user(username)
            if existing is None:  # pragma: no cover - защитный кейс
                raise
            return await self._remnawave.users.update_user(
                UpdateUserRequestDto(
                    uuid=existing.uuid,
                    username=username,
                    **mutable_fields,
                ),
            )

        logger.debug('Subscription created for {}', username)
        return created

    async def _find_user(self, username: str) -> GetUserByUsernameResponseDto | None:
        try:
            return await self._remnawave.users.get_user_by_username(username)
        except NotFoundError:
            return None
