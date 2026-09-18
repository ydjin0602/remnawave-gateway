from app.api.utils.enums.base_enum import BaseENUM


class InternalErrorEnum(BaseENUM):
    INTERNAL_ERROR = 'internal_error'

    BAD_REQUEST = 'bad_request'
    INVALID_VALUE = 'invalid_value'

    UNAUTHORIZED = 'unauthorized'
    TOKEN_EXPIRED = 'token_expired'
    FORBIDDEN = 'forbidden'

    NOT_FOUND = 'not_found'
