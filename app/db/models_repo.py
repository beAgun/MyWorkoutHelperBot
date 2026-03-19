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

    @classmethod
    async def save_unauthorized_user(
        cls,
        session: AsyncSession,
        chat_id: int,
        username: str,
        first_name: str,
        last_name: str,
    ):
        user = User(
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        session.add(user)

    @classmethod
    async def save_authorized_user(
        cls,
        session: AsyncSession,
        chat_id: int,
        username: str,
        first_name: str,
        last_name: str,
        site_user_id: int,
    ):
        user = User(
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            site_user_id=site_user_id,
        )
        session.add(user)


class NotificationsRuleRepo(ModelRepo):
    model = NotificationsRule


class NotificationRepo(ModelRepo):
    model = Notification


class WorkoutRepo(ModelRepo):
    model = Workout
