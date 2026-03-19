from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import app.bot.keyboards as kb
from app.db.models_repo import *
from app.db.database import session_manager


async def is_saved_user(chat_id: int):
    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session=session, chat_id=chat_id)
        return user


async def save_unauthorized_user(event: Message | CallbackQuery):
    async with session_manager() as session:
        await UserRepo.save_unauthorized_user(
            session=session,
            chat_id=event.chat.id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
        )


async def is_linked(chat_id: int):
    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session=session, chat_id=chat_id)
        if user:
            return user.site_user_id
        return None


class PublicAuthMiddleware(BaseMiddleware):

    async def __call__(self, handler, event: Message | CallbackQuery, data):

        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
        else:
            return await handler(event, data)

        if not await is_saved_user(chat_id):
            await save_unauthorized_user(event)
            return

        return await handler(event, data)


class AuthMiddlewareMessage(BaseMiddleware):

    async def __call__(self, handler, event: Message, data):

        if not await is_linked(event.chat.id):
            await event.answer("Сначала привяжите свой аккаунт", reply_markup=kb.link)
            return

        return await handler(event, data)


class AuthMiddlewareCallbackQuery(BaseMiddleware):

    async def __call__(self, handler, event: CallbackQuery, data):

        if not await is_linked(event.message.chat.id):
            await event.answer()
            await event.message.answer(
                "Сначала привяжите свой аккаунт", reply_markup=kb.link
            )
            return

        return await handler(event, data)
