from collections.abc import AsyncGenerator

from dishka import Provider
from dishka import Scope
from dishka import provide
from httpx import AsyncClient
from remnawave import RemnawaveSDK

from app.config import config


class RequestProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def remnawave_client_scope(self) -> RemnawaveSDK:
        """DI Scope для клиента Remnawave API."""
        return RemnawaveSDK(
            base_url=config.remnawave.base_url,
            token=config.remnawave.api_key,
        )

    @provide
    async def http_client_scope(self) -> AsyncGenerator[AsyncClient]:
        """DI Scope для httpx-клиента (проксирование подписки)."""
        async with AsyncClient(
            timeout=config.remnawave.request_timeout,
            follow_redirects=True,
        ) as client:
            yield client
