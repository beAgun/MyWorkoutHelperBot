from app.db.models_repo import (
    UserRepo,
    NotificationRepo,
    WorkoutRepo,
    NotificationsRuleRepo,
    ProcessedEventRepo,
)
from app.db.database import session_manager, AsyncSession
from app.db.models import Notification, Workout, User, NotificationsRule, ProcessedEvent
from datetime import datetime, timedelta, timezone
from logger import logger
from app.infra.telegram_sender import Message, TelegramSender


async def send_msg_workout_changed_by_trainer(
    sender: TelegramSender,
    event_type: str,
    site_user_id: int,
    title: str,
    workout_type: str,
    workout_datetime,
):
    async with session_manager() as session:
        user = await UserRepo.get_user_by_site_id(session, site_user_id)
        text = "Проверьте свой дневник тренировок и спортивных событий! Ваш тренер"
        if event_type.split(".")[1] == "created":
            text = "создал событие"
        elif event_type.split(".")[1] == "deleted":
            text = "удалил событие"
        elif event_type.split(".")[1] == "updated":
            text = "изменил событие"
        text += f": {title}\nТип: {workout_type}\nВремя: {workout_datetime}"
        msg = Message(chat_id=user.chat_id, text=text)
        await sender.send_one(msg)


def build_notifications(
    rules: list[NotificationsRule], user: User, workout: Workout
) -> list[Notification]:
    notifications = []
    for rule in rules:
        notify_at = workout.start_at - timedelta(minutes=rule.offset_minutes)
        if notify_at <= datetime.now(tz=timezone.utc):
            continue
        notification = Notification(
            user=user,
            chat_id=user.chat_id,
            workout=workout,
            rule=rule,
            notify_at=notify_at,
        )
        notifications += [notification]
    return notifications


async def handle_workout_created(
    event_id: int,
    site_user_id: int,
    site_workout_id: int,
    title: str,
    workout_type: str,
    workout_datetime: datetime,
):

    async with session_manager() as session:
        if await ProcessedEventRepo.is_processed_event(session, event_id):
            return

        user = await UserRepo.get_user_by_site_id(session, site_user_id)
        rules = await NotificationsRuleRepo.get_default_rules(session, user_id=user.id)
        if not rules:
            logger.warning(
                f"Trying fetching not existing rules, user_id: {user.id}, site_workout_id: {site_workout_id}"
            )
            return
        workout = Workout(
            user=user,
            start_at=workout_datetime,
            site_workout_id=site_workout_id,
            title=title,
            workout_type=workout_type,
        )
        notifications = build_notifications(rules, user, workout)

        session.add(workout)
        session.add_all(notifications)


async def handle_workout_updated(
    event_id: int,
    site_user_id: int,
    site_workout_id: int,
    title: str,
    workout_type: str,
    workout_datetime: datetime,
):

    async with session_manager() as session:
        if await ProcessedEventRepo.is_processed_event(session, event_id):
            return

        user = await UserRepo.get_user_by_site_id(session, site_user_id)
        workout = await WorkoutRepo.get_by_site_workout_id(session, site_workout_id)
        old_start_at = workout.start_at if workout is not None else None

        rules = (
            workout is not None
            and await NotificationsRuleRepo.get_specific_rules(
                session, user_id=user.id, workout_id=workout.id
            )
        ) or await NotificationsRuleRepo.get_default_rules(session, user_id=user.id)
        if not rules:
            logger.warning(
                f"Trying fetch not existing rules, user_id: {user.id}, site_workout_id: {site_workout_id}"
            )
            return

        updated_workout = await WorkoutRepo.upsert_by_site_workout_id(
            session,
            user.id,
            site_workout_id,
            title=title,
            workout_type=workout_type,
            start_at=workout_datetime,
        )
        if old_start_at == updated_workout.start_at:
            return

        await NotificationRepo.delete_by_workout_id(
            session, workout_id=updated_workout.id
        )

        notifications = build_notifications(rules, user, updated_workout)

        session.add_all(notifications)


async def handle_workout_deleted(event_id: int, site_workout_id: int):

    async with session_manager() as session:
        if await ProcessedEventRepo.is_processed_event(session, event_id):
            return

        workout = await WorkoutRepo.get_by_site_workout_id(session, site_workout_id)
        if workout is None:
            logger.warning(
                f"Trying delete not existing workout, site_workout_id: {site_workout_id}"
            )
            return
        await NotificationRepo.delete_by_workout_id(session, workout_id=workout.id)
        await WorkoutRepo.delete_by_id(session, model_id=workout.id)
