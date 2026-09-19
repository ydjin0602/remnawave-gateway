from json import loads
from typing import Any
from uuid import UUID

from faststream.confluent import KafkaBroker
from loguru import logger
from remnawave import RemnawaveSDK
from remnawave import WebhookUtility
from remnawave.models import UpdateUserBodyDto
from remnawave.models.webhook import UserDto

from app.api.utils.enums.remnawave_ntfy_events import RemnawaveNtfyEvents
from app.api.utils.exceptions import AuthenticationError
from app.api.utils.usecase import Usecase
from app.api.v1.schemas.hook import RemnawaveHookSchema
from app.api.v1.schemas.hook import SoonSubscriptionExpirationSchema
from app.config import config


class RemnawaveHookUsecase(Usecase[RemnawaveHookSchema, None]):
    def __init__(self, kafka_broker: KafkaBroker, remnawave: RemnawaveSDK) -> None:
        self._kafka = kafka_broker
        self._remnawave = remnawave

    async def __call__(self, data: RemnawaveHookSchema) -> None:
        """Проверяет подпись, фильтрует события, публикует в Kafka."""
        try:
            payload = WebhookUtility.parse_webhook(
                body=data.body,
                headers=data.headers,
                webhook_secret=config.remnawave.webhook_secret,
            )
        except ValueError as e:
            # Нет обязательных заголовков x-remnawave-signature/timestamp.
            raise AuthenticationError(message=str(e)) from e

        if payload is None:
            raise AuthenticationError(message='Невалидная подпись хука')

        try:
            event = RemnawaveNtfyEvents(payload.event)

        except ValueError:
            return

        user = payload.data
        if not isinstance(user, UserDto):  # pragma: no cover - защита типов
            logger.warning('Unexpected data type for {}', payload.event)
            return

        meta: dict[str, Any] = loads(data.body).get('meta') or {}

        if event == RemnawaveNtfyEvents.USER_EXPIRED_EVENT:
            await self._remnawave.users.update_user(
                UpdateUserBodyDto(
                    username=user.username,
                    active_internal_squads=[config.remnawave.expires_squad_uuid],
                ),
            )
            logger.debug('User {} moved to expires squad', user.username)
            tempo_days = 0
        else:
            interval_hours = meta.get('expiration')
            if interval_hours is None:
                logger.warning(
                    'user.expiration without meta.expiration for {}',
                    user.username,
                )
                return
            # Ремна шлёт интервал в часах от истечения — переводим в дни.
            tempo_days = interval_hours // 24

        if user.telegram_id is None:
            logger.warning('Hook for {} skipped: no telegram_id', user.username)
            return

        message = SoonSubscriptionExpirationSchema(
            id=UUID(user.short_uuid),
            user_id=user.telegram_id,
            expires_at=user.expire_at,
            tempo_days=tempo_days,
        )
        await self._kafka.publish(
            message.model_dump(mode='json'),
            topic=config.kafka.common_topic,
        )
        logger.info(
            'Expiration event published for {} (tempo_days={})',
            user.username,
            tempo_days,
        )
