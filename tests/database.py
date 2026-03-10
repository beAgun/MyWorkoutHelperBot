from datetime import datetime, timezone, timedelta
from app.db.models import *
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import Base, engine
from config import settings


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

    user = User(chat_id=1356187993, username="test")
    rule = NotificationsRule(user=user, offset_minutes=offset)

    workouts = [
        Workout(name="Силовая на низ", start_at=workout1_start_at),
        Workout(name="Силовая на верх", start_at=workout2_start_at),
        Workout(name="Фитнес-дискотека", start_at=workout3_start_at),
        Workout(start_at=workout4_start_at),
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


if __name__ == "__main__":
    asyncio.run(seed_test_data(1))
