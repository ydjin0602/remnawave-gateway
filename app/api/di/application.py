from dishka import Provider
from dishka import Scope
from dishka import provide
from faststream.confluent import KafkaBroker

from app.config import config


class ApplicationProvider(Provider):
    scope = Scope.APP

    @provide
    async def kafka_broker_scope(self) -> KafkaBroker:
        """DI Scope для KafkaBroker."""
        return KafkaBroker(
            bootstrap_servers=config.kafka.bootstrap_servers,
            # allow_auto_create_topics=False,
        )
