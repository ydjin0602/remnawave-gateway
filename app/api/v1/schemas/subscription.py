from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.api.v1.schemas.base_schema import BaseSchema


class CreateSubscriptionSchema(BaseSchema):
    user_id: int = Field(
        description='tg-id юзера: ключ апсерта и telegramId в ремне',
    )
    traffic_limit: int = Field(
        default=0,
        description='Лимит трафика, ГБ (0 = безлимит)',
    )
    connections_limit: int = Field(
        default=0,
        description='Лимит устройств (0 = безлимит)',
    )
    expires_at: datetime = Field(
        description='Дата истечения подписки.',
    )


class SubscriptionSchema(BaseSchema):
    id: UUID
    user_id: str
    traffic_limit: int
    connections_limit: int
    expires_at: datetime | None
    effective_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class GetSubscriptionSchema(BaseSchema):
    subscription_id: UUID
    user_agent: str = ''
