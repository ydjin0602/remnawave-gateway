from typing import Protocol
from typing import TypeVar

TInputDTO = TypeVar('TInputDTO', contravariant=True)
TOutputDTO = TypeVar('TOutputDTO', covariant=True)


class Usecase(Protocol[TInputDTO, TOutputDTO]):
    """Класс - сервис, в котором будет реализован сценарий бизнес - логики.

    Предназначен для изоляции бизнес - логики от остального кода.
    """

    async def __call__(self, data: TInputDTO) -> TOutputDTO:
        """Абстрактный метод для реализации бизнес - логики."""
        raise NotImplementedError
