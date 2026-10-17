from datetime import UTC
from datetime import date
from datetime import datetime
from itertools import batched

from faststream.confluent import KafkaBroker
from loguru import logger
from remnawave import RemnawaveSDK
from remnawave.enums.users import UserStatus

from app.api.utils.usecase import Usecase
from app.api.v1.schemas.init_repeat_purchase import InitRepeatPurchaseOfferSchema
from app.config import config


class InitRepeatPurchaseUsecase(Usecase[None, None]):
    def __init__(
        self,
        kafka_broker: KafkaBroker,
        remnawave: RemnawaveSDK,
    ) -> None:
        self.kafka_broker = kafka_broker
        self.remnawave = remnawave

    async def __call__(self, data: None = None) -> None:
        """Прогон по всем юзерам → паблиш событий цикла → сводка."""
        today = datetime.now(tz=UTC).date()
        scanned = 0
        payloads: list[dict] = []

        cursor: str | None = None
        while True:
            response = await self.remnawave.users.get_users_stream(
                size=config.remnawave.stream_page_size,
                cursor=cursor,
                status=UserStatus.EXPIRED,
            )
            for user in response.users:
                scanned += 1
                if user.telegram_id is None:
                    continue

                tempo_days = self._tempo_days(
                    expire_at=user.expire_at,
                    today=today,
                )
                if tempo_days is None:
                    continue

                payloads.append(
                    InitRepeatPurchaseOfferSchema(
                        user_id=user.telegram_id,
                        tempo_days=tempo_days,
                        expired_at=user.expire_at,
                    ).model_dump(mode='json'),
                )

            if not response.has_more or response.next_cursor is None:
                break
            cursor = response.next_cursor

        published = 0
        for chunk in batched(payloads, config.common.batch_limit, strict=False):
            try:
                await self.kafka_broker.start()
                await self.kafka_broker.publish_batch(
                    *chunk,
                    topic=config.kafka.init_repeat_purchase_topic,
                )
            except Exception as e:
                logger.warning(
                    'Init repeat purchase: publish failed for chunk '
                    f'({len(chunk)} events): {e}',
                )
                continue
            published += len(chunk)

        logger.info(
            'Init repeat purchase run: scanned={}, published={}',
            scanned,
            published,
        )

    @staticmethod
    def _tempo_days(expire_at: datetime, today: date) -> int | None:
        """Позиция шага в 90-дневном цикле или None (не кандидат)."""
        days = (today - expire_at.date()).days
        if days < config.remnawave.min_days_after_expire:
            return None

        remainder = days % config.remnawave.cycle_period_days
        if remainder == 30:
            return 30
        if remainder == 60:
            return 60
        if remainder == 0:
            return 90
        return None
