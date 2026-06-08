from app.db.database import session_manager
from app.db.models_repo import UserRepo
from logger import logger


async def is_saved_user(chat_id: int):
    async with session_manager() as session:
        return await UserRepo.get_user_by_chat_id(session=session, chat_id=chat_id)


async def save_unauthorized_user(
    chat_id: int, username: str, first_name: str, last_name: str
):
    async with session_manager() as session:
        await UserRepo.save_unauthorized_user(
            session=session,
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )


async def is_linked(chat_id: int) -> int | None:
    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session, chat_id=chat_id)
        return user.site_user_id if user else None


async def user_has_notifications_enabled(site_user_id: int) -> bool:

    async with session_manager() as session:
        user = await UserRepo.get_user_by_site_id(session, site_user_id)

        if not user:
            logger.warning(
                f"Trying fetch not existing user, site_user_id: {site_user_id}"
            )
            return False

        return user.notifications_enabled
