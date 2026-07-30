from ..db.database import session_manager
from datetime import datetime, timezone
import asyncio
from config import settings
from app.infra.telegram_sender import TelegramSender, Message
from app.db.repo import Repo
from app.db.models_repo import CompetitionMonitorStateRepo, UserRepo
from tests.utils import async_timed
from aiohttp.client import ClientSession, ClientTimeout
from app.infra.http_client import HttpClient
from datetime import datetime

local_tz = settings.LOCAL_TZ


def format_date(date: datetime):
    return date.astimezone(local_tz).strftime("%H:%M %d.%m.%Y")


@async_timed()
async def send_trainings_notifications(sender: TelegramSender):
    async with session_manager() as session:
        repo = Repo(session)

        now = datetime.now(tz=timezone.utc)
        data = await repo.get_pending_and_mark_sent_with_workout_data(date=now)
        # print(data)

        formatted_data = [
            Message(
                item.chat_id,
                f"{item.title or 'Тренировка'} начнётся в {format_date(item.start_at)}",
            )
            for item in data
        ]
        await sender.send_batch(formatted_data)


# asyncio.run(send_trainings_notifications())
async def check_kgbrun_registration_open(
    http_session: ClientSession, sender: TelegramSender
):
    response = await http_session.get(
        "/api/events/detailedEvent?Language=ru&EventCode=LegkoatleticheskiyprobegnaKubokGubernatoraSanktPeterburga3Etap"
    )
    # for k, v in response.request_info.headers.items():
    #     print(f"{k}: {v}")
    response.raise_for_status()
    data = await response.json()
    races = [race for race in data.get("races") if race.get("code") in ["10km", "5km"]]
    registrationOpenDates = [
        {
            "code": race.get("code"),
            "name": race.get("name"),
            "date": datetime.fromisoformat(race.get("registrationOpenDate"))
            .replace(tzinfo=timezone.utc)
            .astimezone(tz=local_tz),
        }
        for race in races
    ]
    print(registrationOpenDates)

    now = datetime.now(tz=timezone.utc)
    async with session_manager() as session:
        for event in registrationOpenDates:
            event_row = await CompetitionMonitorStateRepo.get_event_state(
                session, event_code=event.get("code")
            )
            if event_row is None or event_row.registration_date != event.get("date"):
                users = await UserRepo.get_competitions_notifications_subscribed_users(
                    session
                )
                if event_row is None:
                    text = f'Регистрация на мероприятие {event.get("name")} откроется в {event.get("date").strftime("%H:%M %d.%m.%Y")}.'
                else:
                    text = f' Время регистрации на мероприятие {event.get("name")} изменилось: {event.get("date").strftime("%H:%M %d.%m.%Y")}.'
                await sender.send_batch(
                    [Message(chat_id=user.chat_id, text=text) for user in users]
                )
            await CompetitionMonitorStateRepo.upsert_event_state(
                session,
                event_code=event.get("code"),
                registration_date=event.get("date"),
                checked_at=now,
            )


async def create_http_client():
    client = HttpClient(base_url="https://reg.russiarunning.com/")
    session = await client.get_session(
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36 OPR/133.0.0.0"
            ),
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": (
                "https://reg.russiarunning.com/event/"
                "LegkoatleticheskiyprobegnaKubokGubernatoraSanktPeterburga3Etap"
            ),
        }
    )
    return client


async def main():
    client = await create_http_client()
    await check_kgbrun_registration_open(http_session=client.session)
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
