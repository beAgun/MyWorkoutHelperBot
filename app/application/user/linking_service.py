from config import settings
from itsdangerous import URLSafeTimedSerializer
from app.db.database import session_manager
from app.db.models_repo import UserRepo
from logger import logger
from .repository import is_linked
from sqlalchemy.exc import IntegrityError


async def handle_linking(chat_id: int, token: str) -> str:
    """
    returns: answer message
    """
    if await is_linked(chat_id):
        return "Telegram бот уже привязан к аккаунту на сайте."

    try:
        serializer = URLSafeTimedSerializer(secret_key=settings.TG_LINK_TOKEN)
        site_user_id = serializer.loads(token, max_age=600)
    except Exception as e:
        logger.error("Token serialization exception", exc_info=e)
        raise ValueError("Не удалось привязать telegram бот к аккаунту на сайте.")

    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session, chat_id=chat_id)

        if not user:
            raise ValueError("Пользователь не найден.")

        try:
            user.site_user_id = site_user_id
            await session.commit()
        except IntegrityError:
            raise IntegrityError(
                "Telegram бот уже привязан к другому аккаунту на сайте."
            )

        return "Telegram бот успешно привязан к аккаунту на сайте."
