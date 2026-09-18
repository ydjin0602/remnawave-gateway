from dishka import Provider
from dishka import Scope
from dishka import provide

from app.api.v1.usecases.disable_auto_renew import DisableAutoRenewUsecase
from app.api.v1.usecases.get_subscription import GetSubscriptionUsecase
from app.api.v1.usecases.incy_redirect import IncyRedirectUsecase
from app.api.v1.usecases.revoke_subscription import RevokeSubscriptionUsecase
from app.api.v1.usecases.subscribe import SubscribeUsecase


class UsecaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def subscribe_scope(self) -> SubscribeUsecase:
        """DI Scope для SubscribeUsecase."""
        return SubscribeUsecase()

    @provide
    async def get_subscription_scope(self) -> GetSubscriptionUsecase:
        """DI Scope для GetSubscriptionUsecase."""
        return GetSubscriptionUsecase()

    @provide
    async def incy_redirect_scope(self) -> IncyRedirectUsecase:
        """DI Scope для IncyRedirectUsecase."""
        return IncyRedirectUsecase()

    @provide
    async def disable_auto_renew_scope(self) -> DisableAutoRenewUsecase:
        """DI Scope для DisableAutoRenewUsecase."""
        return DisableAutoRenewUsecase()

    @provide
    async def revoke_subscription_scope(self) -> RevokeSubscriptionUsecase:
        """DI Scope для RevokeSubscriptionUsecase."""
        return RevokeSubscriptionUsecase()
