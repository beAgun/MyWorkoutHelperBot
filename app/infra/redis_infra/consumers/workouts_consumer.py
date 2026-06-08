import json
import asyncio
from datetime import datetime
from app.infra.redis_infra.redis_client import redis_client
from app.application.user.repository import user_has_notifications_enabled
from app.application.actions.workouts_events import (
    handle_workout_created,
    handle_workout_updated,
    handle_workout_deleted,
)
from logger import logger

STREAM = "workouts_stream"
GROUP = "notifications_group"
CONSUMER = "notifications_consumer_1"


async def process_event(event_id: int, event_type: str, data: dict):

    site_user_id = data["user_id"]
    if not await user_has_notifications_enabled(site_user_id):
        return

    workout_datetime = datetime.fromisoformat(data["datetime"])

    if event_type == "workout.created":

        await handle_workout_created(
            event_id,
            site_user_id,
            data["workout_id"],
            data["title"],
            data["workout_type"],
            workout_datetime,
        )

    elif event_type == "workout.updated":

        await handle_workout_updated(
            event_id,
            site_user_id,
            data["workout_id"],
            data["title"],
            data["workout_type"],
            workout_datetime,
        )

    elif event_type == "workout.deleted":

        await handle_workout_deleted(event_id, data["workout_id"])


async def process_messages(messages):
    for _, message_list in messages:
        for message_id, fields in message_list:
            try:

                event_id = fields["event_id"]
                event_type = fields["event_type"]
                data = json.loads(fields["data"])
                await process_event(
                    event_id=int(event_id), event_type=event_type, data=data
                )
                await redis_client.xack(STREAM, GROUP, message_id)

            except Exception as e:
                logger.exception(f"Message processing error: {e}")


async def process_pending():
    messages = await redis_client.xreadgroup(
        groupname=GROUP,
        consumername=CONSUMER,
        streams={STREAM: "0"},
    )
    await process_messages(messages)


async def start_consumer():

    logger.info("Notifications consumer started")

    await process_pending()

    while True:
        try:
            messages = await redis_client.xreadgroup(
                groupname=GROUP,
                consumername=CONSUMER,
                streams={STREAM: ">"},
                count=10,
                block=5000,
            )

            if not messages:
                continue

            await process_messages(messages)

        except Exception as e:
            logger.exception(f"Consumer error: {e}")

        await asyncio.sleep(1)
