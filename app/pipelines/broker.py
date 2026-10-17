from dishka.integrations.taskiq import ContainerMiddleware
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisStreamBroker

from app.api.di import DI_CONTAINER
from app.config import config

broker = RedisStreamBroker(
    url=config.redis.broker_url,
    queue_name=config.redis.taskiq_channel_tmp.format(
        project_name=config.common.project_name,
    ),
    consumer_group_name=config.redis.taskiq_consumer_group_name_tmp.format(
        project_name=config.common.project_name,
    ),
    consumer_name=config.redis.taskiq_broker_consumer_tmp.format(
        project_name=config.common.project_name,
    ),
    # At-most-once: XAUTOCLAIM никогда не заберёт unacked-хвосты (нет
    # ретраев/DLQ-редоставок). Краш mid-task оставляет мёртвую PEL-запись —
    # она не доставляется никогда; потерянный день прогона всё равно
    # невосстановим (селектор считает дни от now()).
    idle_timeout=1_000_000_000_000,
)

etl_source = LabelScheduleSource(broker=broker)
broker.add_middlewares(
    ContainerMiddleware(container=DI_CONTAINER),
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[etl_source],
)
