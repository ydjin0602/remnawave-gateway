from datetime import datetime

from pydantic import Field

from app.api.v1.schemas.base_schema import BaseSchema


class InitRepeatPurchaseOfferSchema(BaseSchema):
    """Событие шага цикла 30/60/90 воронки «Инициация повторной покупки».

    Паблишится в общий топик init_repeat_purchase (без знаний о ботах);
    роутинг на бота — в port-users.
    """

    user_id: int = Field(description='tg-id юзера')
    tempo_days: int = Field(description='шаг цикла: 30|60|90')
    expired_at: datetime = Field(description='expire_at подписки (UTC)')
