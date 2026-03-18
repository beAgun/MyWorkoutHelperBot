from .models import *
from .repo import Repo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class ModelRepo:
    model = None

    @classmethod
    async def get_row_by_id(cls, session: AsyncSession, model_id: int):
        query = select(cls.model).filter_by(id=model_id)
        res = await session.execute(query)
        return res.scalar_one_or_none()


class UserRepo(ModelRepo):
    model = User

    @classmethod
    async def get_user_by_chat_id(cls, session: AsyncSession, chat_id: int):
        query = select(cls.model).filter_by(chat_id=chat_id)
        res = await session.execute(query)
        return res.one_or_none()


class NotificationsRuleRepo(ModelRepo):
    model = NotificationsRule


class NotificationRepo(ModelRepo):
    model = Notification


class WorkoutRepo(ModelRepo):
    model = Workout
