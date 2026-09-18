from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.api.v1.schemas.base_schema import BaseSchema


class SoonSubscriptionExpirationSchema(BaseSchema):
    """Сообщение в Kafka — контракт консьюмера vpn-bot, не менять.

    Ровно та же схема, что публиковал vpn-subscriptions
    (SoonSubscriptionExpirationUsecase). DunningStateEnum бота:
    0 = момент истечения, 1/3/5/12/19 = дни после.
    """

    id: UUID = Field(description='uuid юзера ремны')
    user_id: int = Field(description='tg-id юзера')
    expires_at: datetime = Field(description='дата истечения подписки')
    tempo_days: int = Field(description='шаг воронки: 0|1|3|5|12|19')


class RemnawaveHookSchema(BaseSchema):
    """Сырой хук ремны: тело + заголовки (нужны для проверки HMAC)."""

    body: str
    headers: dict[str, str]
