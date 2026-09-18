def get_tags_metadata() -> list[dict]:
    """Генерируем доку для тегов.

    Returns:
        list[dict]

    """

    return [
        # Client
        {
            'name': 'Client',
            'description': 'Клиентские ручки',
        },
        {
            'name': 'Client|Subscriptions',
            'description': 'Подписки',
            'parent': 'Client',
        },
        {
            'name': 'Client|Hooks',
            'description': 'Хуки внешних систем',
            'parent': 'Client',
        },
    ]
