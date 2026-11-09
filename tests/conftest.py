import itertools

from collections.abc import AsyncGenerator
from datetime import datetime
from types import SimpleNamespace
from uuid import UUID
from uuid import uuid4

import pytest

from dishka import Provider
from dishka import Scope
from dishka import make_async_container
from dishka import provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from faststream.confluent import KafkaBroker
from httpx import ASGITransport
from httpx import AsyncClient
from remnawave import RemnawaveSDK
from remnawave.exceptions import ApiErrorResponse
from remnawave.exceptions import NotFoundError
from remnawave.models import UpdateUserBodyDto

from app.api.di.usecase import UsecaseProvider
from app.api.utils.exception_handlers import setup_exception_handlers
from app.api.v1.router import ROUTER as V1_ROUTER
from app.api.v1.usecases.delete_subscription_users import DeleteSubscriptionUsersUsecase
from app.config import config

TEST_API_KEY = 'test-api-key'
EXPIRES_SQUAD_UUID = uuid4()


class FakeRemnawaveUsers:
    """Дак-тайп users-контроллера ремны: только то, что нужно revoke-usecase."""

    def __init__(self) -> None:
        self.users: dict[str, SimpleNamespace] = {}
        self.update_calls: list[UpdateUserBodyDto] = []
        self.deleted_ids: list[int] = []
        self._next_id = itertools.count(1)

    def add_user(
        self,
        username: str,
        expire_at: datetime,
        squads: list[str] | None = None,
    ) -> SimpleNamespace:
        user = SimpleNamespace(
            id=next(self._next_id),
            short_uuid=str(uuid4()),
            username=username,
            expire_at=expire_at,
            active_internal_squads=squads or [],
        )
        self.users[user.short_uuid] = user
        return user

    async def get_user_by_short_uuid(self, short_uuid: str) -> SimpleNamespace:
        try:
            return self.users[short_uuid]
        except KeyError:
            raise NotFoundError(
                404,
                ApiErrorResponse(message='User not found'),
            ) from None

    async def delete_user(self, user_id: int) -> None:
        """Удаляет юзера целиком (по numeric id)."""
        self.deleted_ids.append(user_id)
        self.users = {
            short_uuid: user
            for short_uuid, user in self.users.items()
            if user.id != user_id
        }

    async def update_user(self, body: UpdateUserBodyDto) -> SimpleNamespace:
        self.update_calls.append(body)
        user = next(
            (u for u in self.users.values() if u.username == body.username),
            None,
        )
        if user is None:
            raise NotFoundError(404, ApiErrorResponse(message='User not found'))
        if body.expire_at is not None:
            user.expire_at = body.expire_at
        if body.active_internal_squads is not None:
            user.active_internal_squads = body.active_internal_squads
        return user


class FakeRemnawave:
    def __init__(self) -> None:
        self.users = FakeRemnawaveUsers()


@pytest.fixture(autouse=True)
def _patch_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config.auth, 'api_key', TEST_API_KEY)
    monkeypatch.setattr(config.remnawave, 'expires_squad_uuid', str(EXPIRES_SQUAD_UUID))


@pytest.fixture
def expires_squad_uuid() -> UUID:
    return EXPIRES_SQUAD_UUID


@pytest.fixture
def fake_remnawave() -> FakeRemnawave:
    return FakeRemnawave()


@pytest.fixture
def delete_usecase(fake_remnawave: FakeRemnawave) -> DeleteSubscriptionUsersUsecase:
    return DeleteSubscriptionUsersUsecase(remnawave=fake_remnawave)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {'Authorization': f'Bearer {TEST_API_KEY}'}


@pytest.fixture
async def client(fake_remnawave: FakeRemnawave):
    class FakeRemnawaveProvider(Provider):
        scope = Scope.REQUEST

        @provide
        def remnawave_client_scope(self) -> RemnawaveSDK:
            return fake_remnawave  # type: ignore[return-value]

        @provide
        def kafka_broker_scope(self) -> KafkaBroker:
            return SimpleNamespace()  # type: ignore[return-value]

        @provide
        async def http_client_scope(self) -> AsyncGenerator[AsyncClient]:
            async with AsyncClient() as http:
                yield http

    app = FastAPI(default_response_class=ORJSONResponse)
    setup_exception_handlers(app)
    app.include_router(V1_ROUTER)
    container = make_async_container(UsecaseProvider(), FakeRemnawaveProvider())
    setup_dishka(container=container, app=app)

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as async_client:
        yield async_client
    await container.close()
