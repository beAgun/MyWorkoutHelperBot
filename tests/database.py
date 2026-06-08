from datetime import datetime, timezone, timedelta
from app.db.models import *
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import Base, engine
from config import settings
from app.db.database import session_manager


async def prepare_test_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def seed_test_data(session: AsyncSession):

    now = datetime.now(tz=timezone.utc)
    offset = 10
    workout1_start_at = now + timedelta(minutes=offset) - timedelta(minutes=1)
    workout2_start_at = now + timedelta(minutes=offset)
    workout3_start_at = now + timedelta(minutes=offset) + timedelta(minutes=1)
    workout4_start_at = now + timedelta(minutes=offset) + timedelta(minutes=2)

    user = User(
        chat_id=1356187993, username="test", site_user_id=1, notifications_enabled=True
    )
    rule = NotificationsRule(user=user, offset_minutes=offset)

    workouts = [
        Workout(
            title="Силовая на низ",
            start_at=workout1_start_at,
            site_workout_id=1,
            user=user,
        ),
        Workout(
            title="Силовая на верх",
            start_at=workout2_start_at,
            site_workout_id=2,
            user=user,
        ),
        Workout(
            title="Фитнес-дискотека",
            start_at=workout3_start_at,
            site_workout_id=3,
            user=user,
        ),
        Workout(start_at=workout4_start_at, site_workout_id=4, user=user),
    ]

    notifications = [
        Notification(
            user=user,
            chat_id=user.chat_id,
            workout=workouts[0],
            rule=rule,
            notify_at=workout1_start_at - timedelta(minutes=offset),
        ),
        Notification(
            user=user,
            chat_id=user.chat_id,
            workout=workouts[1],
            rule=rule,
            notify_at=workout2_start_at - timedelta(minutes=offset),
        ),
        Notification(
            user=user,
            chat_id=user.chat_id,
            workout=workouts[2],
            rule=rule,
            notify_at=workout3_start_at - timedelta(minutes=offset),
        ),
        Notification(
            user=user,
            chat_id=user.chat_id,
            workout=workouts[3],
            rule=rule,
            notify_at=workout4_start_at - timedelta(minutes=offset),
        ),
    ]

    session.add(user)
    session.add(rule)
    session.add_all(workouts)
    session.add_all(notifications)


async def test_seed_database():
    await prepare_test_database()
    async with session_manager() as session:
        await seed_test_data(session)


if __name__ == "__main__":
    asyncio.run(test_seed_database())
