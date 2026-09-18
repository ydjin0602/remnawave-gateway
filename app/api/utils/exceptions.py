from starlette import status

from app.api.utils.enums.internal_exception_status_enum import InternalErrorEnum


class BaseError(Exception):
    message: str
    internal_status_code: InternalErrorEnum | None = None
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str,
        internal_status_code: InternalErrorEnum | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        self.internal_status_code = (
            internal_status_code or InternalErrorEnum.INTERNAL_ERROR
        )
        self.status_code = status_code

    def __str__(self) -> str:
        return f'{self.__class__.__name__}: {self.message}'

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'message={self.message},'
            f' internal_status_code={self.internal_status_code},'
            f' status_code={self.status_code}'
            f')'
        )


class AuthenticationError(BaseError):
    def __init__(
        self,
        message: str,
        internal_status_code: InternalErrorEnum = InternalErrorEnum.UNAUTHORIZED,
    ) -> None:
        super().__init__(
            message=f'Ошибка аутентификации: {message}',
            internal_status_code=internal_status_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class NotFoundError(BaseError):
    def __init__(
        self,
        message: str,
        internal_status_code: InternalErrorEnum = InternalErrorEnum.NOT_FOUND,
    ) -> None:
        super().__init__(
            message=message,
            internal_status_code=internal_status_code,
            status_code=status.HTTP_404_NOT_FOUND,
        )
