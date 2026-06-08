from app.tasks.celery_app import celery_app
from app.infra.site_client import SiteClient
from app.db.models import Workout, NotificationsRule
from app.db.database import session_manager
from app.db.models_repo import (
    UserRepo,
    NotificationsRuleRepo,
    NotificationRepo,
    WorkoutRepo,
)
from app.domain.notifications.notification_time import NotificationTime
from app.application.actions.workouts_events import build_notifications
from logger import logger
import asyncio
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone


async def create_user_notifications(chosen_times: list[int], chat_id: int):

    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id_and_enable_notifications(
            session=session, chat_id=chat_id
        )
        logger.info(
            f"chat_id={chat_id}, user_id={user.id if user is not None else None}"
        )
        if user is None:
            logger.warning(
                f"Notifications are already enabled for chat_id: {chat_id} or not existing user"
            )
            return

        async with SiteClient() as site_session:
            data = await site_session.get_user_workouts(user_id=user.site_user_id)
        workouts_data = data.workouts
        rules, workouts, notifications = [], [], []

        for offset_minutes in chosen_times:
            rule = NotificationsRule(
                user=user,
                offset_minutes=offset_minutes,
            )
            rules.append(rule)

        for workout in workouts_data:
            workout = Workout(
                user=user,
                site_workout_id=workout.id,
                start_at=workout.workout_datetime,
                title=workout.title,
                workout_type=workout.workout_type,
            )
            workouts.append(workout)
            notifications.extend(build_notifications(rules, user, workout))

        session.add_all(rules)
        session.add_all(workouts)
        session.add_all(notifications)


async def edit_user_notifications(chosen_times: list[int], chat_id: int):

    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session=session, chat_id=chat_id)
        logger.info(
            f"chat_id={chat_id}, user_id={user.id if user is not None else None}"
        )
        if user is None or not user.notifications_enabled:
            logger.warning(
                f"Notifications are not enabled for chat_id: {chat_id} or not existing user"
            )
            return

        await NotificationsRuleRepo.delete_all_user_rules(session, user_id=user.id)
        rules, notifications = [], []

        for offset_minutes in chosen_times:
            rule = NotificationsRule(
                user=user,
                offset_minutes=offset_minutes,
            )
            rules.append(rule)

        await NotificationRepo.delete_all_by_user_id(session, user_id=user.id)
        from_datetime = datetime.now(timezone.utc)
        workouts = await WorkoutRepo.get_all_by_user_id_from_datetime(
            session, user_id=user.id, from_datetime=from_datetime
        )
        for workout in workouts:
            notifications.extend(build_notifications(rules, user, workout))

        session.add_all(rules)
        session.add_all(notifications)


async def delete_user_notifications(chat_id: int):
    async with session_manager() as session:
        user_id = await UserRepo.disable_notifications_by_chat_id(
            session=session, chat_id=chat_id
        )
        if user_id is None:
            logger.warning(
                f"Trying delete notifications for not existing user, chat_id: {chat_id}"
            )
            return

        await WorkoutRepo.delete_by_user_id(
            session,
            user_id=user_id,
        )
        await NotificationsRuleRepo.delete_all_user_rules(session, user_id=user_id)


@celery_app.task(
    autoretry_for=(Exception,),
    dont_autoretry_for=(IntegrityError,),
    retry_backoff=True,
)
def create_user_notifications_task(chosen_times: list[int], chat_id: int):
    try:
        asyncio.run(create_user_notifications(chosen_times, chat_id))
    except Exception as e:
        logger.exception(e)


@celery_app.task(
    autoretry_for=(Exception,),
    dont_autoretry_for=(IntegrityError,),
    retry_backoff=True,
)
def edit_user_notifications_task(chosen_times: list[int], chat_id: int):
    try:
        asyncio.run(edit_user_notifications(chosen_times, chat_id))
    except Exception as e:
        logger.exception(e)


@celery_app.task(
    autoretry_for=(Exception,),
    dont_autoretry_for=(IntegrityError,),
    retry_backoff=True,
)
def delete_user_notifications_task(chat_id: int):
    try:
        asyncio.run(delete_user_notifications(chat_id))
    except Exception as e:
        logger.exception(e)
