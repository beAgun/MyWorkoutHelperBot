from app.db.database import session_manager
from app.db.models_repo import UserRepo


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


async def is_linked(chat_id: int):
    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session, chat_id=chat_id)
        return user.site_user_id if user else None
