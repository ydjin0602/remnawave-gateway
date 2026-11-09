"""DELETE /sub/: полное удаление юзеров из remnawave по short_uuid подписок."""

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import UUID

from app.api.v1.schemas.subscription import DeleteSubscriptionsSchema


async def test_delete_removes_user_entirely(
    delete_usecase,
    fake_remnawave,
):
    user = fake_remnawave.users.add_user(
        username='111',
        expire_at=datetime.now(tz=UTC) + timedelta(days=30),
    )

    await delete_usecase(
        data=DeleteSubscriptionsSchema(subscription_ids=[UUID(user.short_uuid)]),
    )

    # Юзер удалён целиком, а не переведён в истёкшее состояние.
    assert fake_remnawave.users.deleted_ids == [user.id]
    assert user.short_uuid not in fake_remnawave.users.users
    assert fake_remnawave.users.update_calls == []


async def test_delete_same_id_twice_is_ok(
    delete_usecase,
    fake_remnawave,
):
    user = fake_remnawave.users.add_user(
        username='111',
        expire_at=datetime.now(tz=UTC) + timedelta(days=30),
    )
    payload = DeleteSubscriptionsSchema(
        subscription_ids=[UUID(user.short_uuid)],
    )

    await delete_usecase(data=payload)
    await delete_usecase(data=payload)

    # Второй вызов — идемпотентный skip (юзера уже нет).
    assert fake_remnawave.users.deleted_ids == [user.id]


async def test_delete_does_not_touch_other_users(
    delete_usecase,
    fake_remnawave,
):
    other_expire_at = datetime.now(tz=UTC) + timedelta(days=30)
    target = fake_remnawave.users.add_user(
        username='111',
        expire_at=datetime.now(tz=UTC) + timedelta(days=30),
    )
    other = fake_remnawave.users.add_user(
        username='222',
        expire_at=other_expire_at,
    )

    await delete_usecase(
        data=DeleteSubscriptionsSchema(subscription_ids=[UUID(target.short_uuid)]),
    )

    assert fake_remnawave.users.deleted_ids == [target.id]
    assert other.expire_at == other_expire_at
    assert other.short_uuid in fake_remnawave.users.users


async def test_delete_unknown_id_is_ok(
    delete_usecase,
    fake_remnawave,
):
    """Несуществующий short_uuid — тихий skip (идемпотентность мержа)."""
    await delete_usecase(
        data=DeleteSubscriptionsSchema(subscription_ids=[UUID(int=0)]),
    )

    assert fake_remnawave.users.deleted_ids == []
