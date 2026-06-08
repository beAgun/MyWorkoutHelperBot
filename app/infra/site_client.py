from aiohttp.client import ClientSession, ClientTimeout
from config import settings
from datetime import datetime, timezone
from .site_schemas import UserWorkoutsDTO
from logger import logger


class SiteClient:
    def __init__(self):
        self.base_url = f"{settings.WORKOUT_SITE_URL}"
        self.timeout = ClientTimeout(total=10)
        self.session = None

    async def __aenter__(self):
        self.session = ClientSession(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"X-API-KEY": settings.SITE_TG_API_KEY},
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def send_email_link(self, email: str, chat_id: int):
        data = {"email": email, "chat_id": chat_id}

        response = await self.session.post("/notifications/email-tg-link/", json=data)

        return response

    async def get_user_workouts(self, user_id: int):
        data = {
            "user_id": user_id,
            "from_datetime": datetime.now(timezone.utc).isoformat(),
        }

        try:
            response = await self.session.post(
                "/notifications/get-user-workouts/",
                json=data,
            )
            data = await response.json()
            return UserWorkoutsDTO(**data)
        except Exception as error:
            logger.error(
                f"Fetching workouts for user {user_id} ended with error {str(error)}"
            )

    async def close(self):
        await self.session.close()
