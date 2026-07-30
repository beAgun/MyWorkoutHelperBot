from .models import (
    Base,
    User,
    NotificationsRule,
    Notification,
    Workout,
    ProcessedEvent,
    CompetitionMonitorState,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, exists, distinct
from sqlalchemy.dialects.postgresql import insert
from typing import TypeVar, Generic
from datetime import datetime

_T = TypeVar("_T", bound=Base)


class ModelRepo(Generic[_T]):
    model: type[_T] = None

    @classmethod
    async def get_row_by_id(cls, session: AsyncSession, model_id: int) -> _T | None:
        query = select(cls.model).filter_by(id=model_id)
        res = await session.execute(query)
        return res.scalar_one_or_none()

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, model_id: int) -> None:
        query = delete(cls.model).where(cls.model.id == model_id)
        await session.execute(query)


class UserRepo(ModelRepo):
    model = User

    @classmethod
    async def get_user_by_chat_id(
        cls, session: AsyncSession, chat_id: int
    ) -> _T | None:
        query = select(cls.model).filter_by(chat_id=chat_id)
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @classmethod
    async def get_user_by_site_id(
        cls, session: AsyncSession, site_user_id: int
    ) -> _T | None:
        query = select(cls.model).filter_by(site_user_id=site_user_id)
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @classmethod
    async def save_unauthorized_user(
        cls,
        session: AsyncSession,
        chat_id: int,
        username: str,
        first_name: str,
        last_name: str,
    ) -> None:
        user = User(
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        session.add(user)

    @classmethod
    async def get_user_by_chat_id_and_enable_notifications(
        cls, session: AsyncSession, chat_id: int
    ) -> _T | None:
        query = (
            update(cls.model)
            .where(
                cls.model.chat_id == chat_id,
                cls.model.notifications_enabled.is_(False),
            )
            .values(notifications_enabled=True)
            .returning(cls.model)
        )
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @classmethod
    async def disable_notifications_by_chat_id(
        cls, session: AsyncSession, chat_id: int
    ) -> _T | None:
        query = (
            update(cls.model)
            .where(cls.model.chat_id == chat_id)
            .values(notifications_enabled=False)
        ).returning(cls.model.id)
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @classmethod
    async def get_competitions_notifications_subscribed_users(
        cls, session: AsyncSession
    ) -> list[_T]:
        query = select(cls.model).where(cls.model.competitions_notifications.is_(True))
        res = await session.execute(query)
        return res.scalars().all()


class NotificationsRuleRepo(ModelRepo):
    model = NotificationsRule

    @classmethod
    async def get_specific_rules(
        cls, session: AsyncSession, user_id: int, workout_id: int
    ) -> list[_T]:
        query = select(cls.model).where(
            cls.model.user_id == user_id,
            cls.model.workout_id == workout_id,
        )

        res = await session.execute(query)
        return res.scalars().all()

    @classmethod
    async def get_default_rules(cls, session: AsyncSession, user_id: int) -> list[_T]:
        query = select(cls.model).where(
            cls.model.user_id == user_id,
            cls.model.workout_id.is_(None),
        )

        res = await session.execute(query)
        return res.scalars().all()

    @classmethod
    async def get_all_user_rules(cls, session: AsyncSession, user_id: int) -> list[_T]:
        query = select(cls.model).where(
            cls.model.user_id == user_id,
        )

        res = await session.execute(query)
        return res.scalars().all()

    @classmethod
    async def delete_all_user_rules(cls, session: AsyncSession, user_id: int) -> None:
        query = delete(cls.model).where(
            cls.model.user_id == user_id,
        )

        res = await session.execute(query)
        return

    @classmethod
    async def rules_exist(cls, session: AsyncSession, user_id: int) -> bool:
        query = select(exists().where(cls.model.user_id == user_id))

        res = await session.execute(query)
        return res.scalar()


class NotificationRepo(ModelRepo):
    model = Notification

    @classmethod
    async def delete_all_by_user_id(cls, session: AsyncSession, user_id: int) -> None:
        query = delete(cls.model).where(cls.model.user_id == user_id)
        await session.execute(query)

    @classmethod
    async def delete_by_workout_id(cls, session: AsyncSession, workout_id: int) -> None:
        query = delete(cls.model).where(cls.model.workout_id == workout_id)
        await session.execute(query)

    @classmethod
    async def get_workouts_ids_by_user_id(
        cls, session: AsyncSession, user_id: int
    ) -> list[_T]:
        query = select(distinct(cls.model.workout_id)).where(
            cls.model.user_id == user_id
        )

        res = await session.execute(query)
        return res.scalars().all()


class WorkoutRepo(ModelRepo):
    model = Workout

    @classmethod
    async def get_by_site_workout_id(
        cls, session: AsyncSession, site_workout_id: int
    ) -> _T | None:
        query = select(cls.model).filter_by(site_workout_id=site_workout_id)
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @classmethod
    async def update_by_site_workout_id(
        cls,
        session: AsyncSession,
        site_workout_id: int,
        title: str,
        workout_type: str,
        start_at: datetime,
    ) -> _T | None:
        query = (
            update(cls.model)
            .where(cls.model.site_workout_id == site_workout_id)
            .values(
                title=title,
                workout_type=workout_type,
                start_at=start_at,
            )
            .returning(cls.model)
        )

        res = await session.execute(query)
        return res.scalars().one_or_none()

    @classmethod
    async def upsert_by_site_workout_id(
        cls,
        session: AsyncSession,
        user_id: int,
        site_workout_id: int,
        title: str,
        workout_type: str,
        start_at: datetime,
    ) -> _T | None:
        query = insert(cls.model).values(
            user_id=user_id,
            title=title,
            workout_type=workout_type,
            start_at=start_at,
            site_workout_id=site_workout_id,
        )
        query = (
            query.on_conflict_do_update(
                index_elements=[cls.model.site_workout_id],
                set_={
                    "user_id": user_id,
                    "title": title,
                    "workout_type": workout_type,
                    "start_at": start_at,
                },
            )
            .returning(cls.model)
            .execution_options(populate_existing=True)
        )

        res = await session.execute(query)
        return res.scalars().one_or_none()

    @classmethod
    async def delete_by_ids(cls, session: AsyncSession, ids: list[int]) -> None:
        query = delete(cls.model).where(cls.model.id.in_(ids))
        res = await session.execute(query)
        return

    @classmethod
    async def delete_by_user_id(cls, session: AsyncSession, user_id: int) -> None:
        query = delete(cls.model).where(cls.model.user_id == user_id)
        res = await session.execute(query)
        return

    @classmethod
    async def get_all_by_ids_from_datetime(
        cls, session: AsyncSession, ids: list[int], from_datetime: datetime
    ) -> list[_T]:
        query = select(cls.model).where(
            cls.model.id.in_(ids), cls.model.start_at >= from_datetime
        )
        res = await session.execute(query)
        return res.scalars().all()

    @classmethod
    async def get_all_by_user_id_from_datetime(
        cls, session: AsyncSession, user_id: int, from_datetime: datetime
    ) -> list[_T]:
        query = select(cls.model).where(
            cls.model.user_id == user_id, cls.model.start_at >= from_datetime
        )
        res = await session.execute(query)
        return res.scalars().all()


class ProcessedEventRepo(ModelRepo):
    model = ProcessedEvent

    @classmethod
    async def is_processed_event(cls, session: AsyncSession, event_id: int) -> bool:
        stmt = insert(cls.model).values(id=event_id).on_conflict_do_nothing()

        res = await session.execute(stmt)

        if res.rowcount == 0:
            return True
        return False


class CompetitionMonitorStateRepo(ModelRepo):
    model = CompetitionMonitorState

    @classmethod
    async def get_event_state(
        cls,
        session: AsyncSession,
        event_code: str,
    ) -> _T | None:
        stmt = select(cls.model).where(cls.model.event_code == event_code)

        res = await session.execute(stmt)
        return res.scalars().one_or_none()

    @classmethod
    async def upsert_event_state(
        cls,
        session: AsyncSession,
        event_code: str,
        registration_date: datetime,
        checked_at: datetime,
    ) -> _T | None:
        stmt = (
            insert(cls.model)
            .values(
                event_code=event_code,
                registration_date=registration_date,
                checked_at=checked_at,
            )
            .on_conflict_do_update(
                index_elements=[cls.model.event_code],
                set_={
                    "registration_date": registration_date,
                    "checked_at": checked_at,
                },
            )
        )

        res = await session.execute(stmt)
