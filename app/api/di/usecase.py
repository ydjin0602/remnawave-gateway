from dishka import Provider
from dishka import Scope
from dishka import provide
from faststream.confluent import KafkaBroker
from httpx import AsyncClient
from remnawave import RemnawaveSDK

from app.api.v1.usecases.get_subscription import GetSubscriptionUsecase
from app.api.v1.usecases.incy_redirect import IncyRedirectUsecase
from app.api.v1.usecases.remnawave_hook import RemnawaveHookUsecase
from app.api.v1.usecases.subscribe import SubscribeUsecase


class UsecaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def subscribe_scope(self, remnawave: RemnawaveSDK) -> SubscribeUsecase:
        """DI Scope для SubscribeUsecase."""
        return SubscribeUsecase(remnawave=remnawave)

    @provide
    async def get_subscription_scope(
        self,
        remnawave: RemnawaveSDK,
        http: AsyncClient,
    ) -> GetSubscriptionUsecase:
        """DI Scope для GetSubscriptionUsecase."""
        return GetSubscriptionUsecase(remnawave=remnawave, http=http)

    @provide
    async def remnawave_hook_scope(
        self,
        kafka_broker: KafkaBroker,
    ) -> RemnawaveHookUsecase:
        """DI Scope для RemnawaveHookUsecase."""
        return RemnawaveHookUsecase(kafka_broker=kafka_broker)

    @provide
    async def incy_redirect_scope(self) -> IncyRedirectUsecase:
        """DI Scope для IncyRedirectUsecase."""
        return IncyRedirectUsecase()
