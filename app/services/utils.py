from config import settings
from itsdangerous import URLSafeTimedSerializer
from aiogram.types import Message
from app.db.models import *
from app.db.database import session_manager
from logger import logger
from email_validator import validate_email, EmailNotValidError


async def handle_linking(message: Message, token: str) -> str:
    """
    returns: answer message
    """
    try:
        serializer = URLSafeTimedSerializer(secret_key=settings.TG_LINK_TOKEN)
        user_id = serializer.loads(token, max_age=600)
    except Exception as e:
        logger.info("Token serialization exception", exc_info=e)
        return "Не удалось привязать telegram бот к аккаунту на сайте"

    async with session_manager() as session:
        user = User(
            id=user_id,
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        session.add(user)
    return "Telegram бот успешно привязан к аккаунту на сайте"


def validate_user_email(email: str):
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError:
        return None
