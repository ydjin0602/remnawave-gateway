from datetime import datetime
from uuid import UUID

from pydantic import Field
from pydantic import field_validator

from app.api.utils.enums.app_enum import AppEnum
from app.api.v1.schemas.base_schema import BaseSchema


class CreateSubscriptionSchema(BaseSchema):
    user_id: str = Field(
        default='VPN-PORT-12345678',
        description='Сервис абстрактный, пользователи могут быть из разных '
        'систем, сервис прокси до этой апи обязан соблюсти '
        'шаблон {PARTNER_NAME}-{USER_ID}',
    )
    traffic_limit: int = Field(
        default=0,
        description='Лимит на потребление трафика',
    )
    connections_limit: int = Field(
        default=0,
        description='Лимит на подключения',
    )
    expires_at: datetime | None = Field(
        default=None,
        description='Дата истечения подписки.',
    )


class SubscriptionSchema(BaseSchema):
    id: UUID
    user_id: str
    traffic_limit: int
    connections_limit: int
    expires_at: datetime | None
    grace_expires_at: datetime | None = None
    effective_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class GetSubscriptionSchema(BaseSchema):
    subscription_id: UUID
    app: AppEnum = AppEnum.HAPP


class RevokeSubscriptionsSchema(BaseSchema):
    subscription_ids: list[UUID]


class RefreshSubscriptionConfigSchema(BaseSchema):
    subscription_id: UUID
    config_id: UUID


class SoonSubscriptionExpirationSchema(BaseSchema):
    id: UUID
    user_id: int
    expires_at: datetime
    tempo_days: int

    @field_validator('user_id', mode='before')
    @classmethod
    def add_prefix(cls, value: str | int) -> int:
        """Добавляем сервисный префикс."""
        if isinstance(value, int):
            return value
        return int(value.split('-')[-1])
