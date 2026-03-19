from config import settings
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from aiogram.types import Message
from app.db.models import *
from app.db.database import session_manager
from app.db.models_repo import *
from logger import logger
from email_validator import validate_email, EmailNotValidError
from aiogram.fsm.context import FSMContext
from aiohttp import ClientSession
from fastapi import HTMLResponse


async def handle_linking(message: Message, token: str) -> str:
    """
    returns: answer message
    """
    try:
        serializer = URLSafeTimedSerializer(secret_key=settings.TG_LINK_TOKEN)
        site_user_id = serializer.loads(token, max_age=600)
    except Exception as e:
        logger.info("Token serialization exception", exc_info=e)
        return "Не удалось привязать telegram бот к аккаунту на сайте"

    async with session_manager() as session:
        await UserRepo.save_authorized_user(
            session=session,
            chat_id=message.chat.id
            username=message.from_user.username
            first_name=message.from_user.first_name
            last_name=message.from_user.last_name
            site_user_id=site_user_id
        )
    return "Telegram бот успешно привязан к аккаунту на сайте"


def validate_user_email(email: str):
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError:
        return None


async def check_attempts(
    state: FSMContext, key: str = "ATTEMPTS", max_attempts: int = 5
) -> bool:

    data = await state.get_data()
    attempts = data.get(key, 0)

    if attempts >= max_attempts:
        return False

    await state.update_data(**{key: attempts + 1})
    return True


async def get_email_link(email: str, chat_id: int) -> str:
    data = {"email": email, "chat_id": chat_id, "purpose": "telegram_link"}

    async with ClientSession() as session:
        response = await session.post(
            url=f"{settings.WORKOUT_SITE_URL}/notifications/email-tg-link",
            json=data
        )

        if response.status == 200:
            return "Проверьте почту и перейдите по ссылке для завершения привязки аккаунтов"

        elif response.status == 404:
            return "Пользователь с указанной почтой не найден. Проверьте корректность и попробуйте снова"

        else:
            return "Произошла ошибка"


async def resolve_token(token: str):
    serializer = URLSafeTimedSerializer(secret_key=settings.TG_LINK_TOKEN)

    try:
        data = serializer.loads(token, max_age=600)
    except (BadSignature, SignatureExpired):
        return HTMLResponse("<h1>Ссылка недействительна или устарела</h1>")

    site_user_id = data["site_user_id"]
    chat_id = data["chat_id"]

    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session, chat_id=chat_id)

        if not user:
            return HTMLResponse("<h1>Пользователь не найден</h1>")

        user.site_user_id = site_user_id
        await session.commit()

    return HTMLResponse("<h1>Аккаунт успешно привязан ✅</h1>")
