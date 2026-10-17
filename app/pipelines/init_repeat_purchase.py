from dishka import FromDishka as Depends
from dishka.integrations.taskiq import inject
from loguru import logger

from app.api.v1.usecases.init_repeat_purchase import InitRepeatPurchaseUsecase
from app.config import config
from app.pipelines.broker import broker


@broker.task(
    task_name='INIT_REPEAT_PURCHASE',
    schedule=[
        {
            'cron': config.cron.init_repeat_purchase,
        },
    ],
)
@inject(patch_module=True)
async def init_repeat_purchase_task(
    usecase: Depends[InitRepeatPurchaseUsecase],
) -> None:
    """Крон цикла 30/60/90 «Инициация повторной покупки».

    Итерирует истёкших юзеров ремны (status=EXPIRED, курсорная пагинация),
    отбирает истёкших ≥30 дней по mod 90 и публикует события в общий топик.
    """
    logger.info('Запускаю крон цикла 30/60/90 «Инициация повторной покупки»')
    summary = await usecase()
    logger.success(
        f'Цикл 30/60/90: просканировано {summary["scanned"]} юзеров, '
        f'опубликовано {summary["published"]} событий'
    )
