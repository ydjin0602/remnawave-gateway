"""Taskiq-воркеры и крон-таски remnawave-gateway."""

from app.pipelines.init_repeat_purchase import init_repeat_purchase_task

__all__ = [
    'init_repeat_purchase_task',
]
