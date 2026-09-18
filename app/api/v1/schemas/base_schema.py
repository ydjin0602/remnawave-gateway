"""Базовая схема ORJSON, которую можно использовать как базовую pydantic схему."""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.api.utils.enums.internal_exception_status_enum import InternalErrorEnum


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, validate_assignment=True, from_attributes=True
    )


class ErrorSchema(BaseSchema):
    message: str = Field(description='Сообщение об ошибке')
    code: InternalErrorEnum = Field(description='Системный код ошибки')
