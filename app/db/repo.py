from sqlalchemy import select, and_, update
from sqlalchemy.orm import query
from .models import *
from datetime import datetime
from tests.utils import async_timed


class Repo:

    def __init__(self, session):
        self.session = session

    @async_timed()
    async def get_pending_and_mark_sent_with_workout_data(self, date: datetime):
        updated = (
            update(Notification)
            .filter(and_(Notification.notify_at <= date, Notification.sent.is_(False)))
            .values(sent=True)
            .returning(
                Notification.id,
                Notification.chat_id,
                Notification.notify_at,
                Notification.workout_id,
            )
        ).cte("updated")
        query = select(updated, Workout.name, Workout.start_at).join_from(
            updated, Workout, updated.c.workout_id == Workout.id
        )
        res = await self.session.execute(query)
        rows = res.all()
        return rows

    @async_timed()
    async def get_pending_and_mark_sent(self, date: datetime):
        res = await self.session.execute(
            update(Notification)
            .filter(and_(Notification.notify_at <= date, Notification.sent.is_(False)))
            .values(sent=True)
            .returning(Notification.id, Notification.chat_id, Notification.notify_at)
        )
        rows = res.all()
        return rows

    async def get_pending(self, date: datetime):
        res = await self.session.execute(
            select(
                Notification.id, Notification.chat_id, Notification.notify_at
            ).filter(and_(Notification.notify_at <= date, Notification.sent.is_(False)))
        )
        rows = res.all()
        return rows

    async def mark_sent(self, ids: list[int]):
        await self.session.execute(
            update(Notification).where(Notification.id.in_(ids)).values(sent=True)
        )
