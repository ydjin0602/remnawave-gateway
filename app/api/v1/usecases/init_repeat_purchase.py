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

CYCLE_PERIOD_DAYS = 90
MIN_DAYS_AFTER_EXPIRE = 30
STREAM_PAGE_SIZE = 1000


class InitRepeatPurchaseUsecase(Usecase[None, dict[str, int]]):
    """Продюсер цикла 30/60/90 «Инициация повторной покупки».

    Итерирует истёкших юзеров ремны курсорной пагинацией (GET /users/stream,
    фильтр status=EXPIRED — активных панель не отдаёт), отбирает истёкших
    ≥30 дней назад по mod 90 и публикует события в общий топик.
    Про ботов ничего не знает — роутинг в port-users.
    """

    def __init__(
        self,
        kafka_broker: KafkaBroker,
        remnawave: RemnawaveSDK,
    ) -> None:
        self._kafka = kafka_broker
        self._remnawave = remnawave

    async def __call__(self, data: None = None) -> dict[str, int]:
        """Прогон по всем юзерам → паблиш событий цикла → сводка."""
        today = datetime.now(tz=UTC).date()
        scanned = 0
        payloads: list[dict] = []

        cursor: str | None = None
        while True:
            response = await self._remnawave.users.get_users_stream(
                size=STREAM_PAGE_SIZE,
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
                await self._kafka.start()
                await self._kafka.publish_batch(
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
        return {'scanned': scanned, 'published': published}

    @staticmethod
    def _tempo_days(expire_at: datetime, today: date) -> int | None:
        """Позиция шага в 90-дневном цикле или None (не кандидат)."""
        days = (today - expire_at.date()).days
        if days < MIN_DAYS_AFTER_EXPIRE:
            return None

        remainder = days % CYCLE_PERIOD_DAYS
        if remainder == 30:
            return 30
        if remainder == 60:
            return 60
        if remainder == 0:
            return 90
        return None
