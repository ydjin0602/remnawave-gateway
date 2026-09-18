from dishka import Provider
from dishka import Scope


class RequestProvider(Provider):
    scope = Scope.REQUEST

    # @provide
    # async def remnawave_client_scope(self):
    #     pass
