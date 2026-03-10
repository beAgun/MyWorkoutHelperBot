from ..db.database import session_manager
from datetime import datetime, timezone
import asyncio
from config import settings
from app.infra.telegram_sender import TelegramSender, Message
from app.db.repo import Repo
from tests.utils import async_timed


local_tz = settings.LOCAL_TZ


def format_date(date: datetime):
    return date.astimezone(local_tz).strftime("%H:%M %d.%m.%Y")


@async_timed()
async def send_trainings_notifications(bot):
    async with session_manager() as session:
        repo = Repo(session)
        sender = TelegramSender(bot)

        now = datetime.now(tz=timezone.utc)
        data = await repo.get_pending_and_mark_sent_with_workout_data(date=now)
        # print(data)

        formatted_data = [
            Message(
                item.chat_id,
                f"{item.name or 'Тренировка'} начнётся в {format_date(item.start_at)}",
            )
            for item in data
        ]
        await sender.send_batch(formatted_data)


# asyncio.run(send_trainings_notifications())
