from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import app.bot.keyboards as kb
from app.db.models_repo import *
from app.application.user.repository import (
    is_saved_user,
    save_unauthorized_user,
    is_linked,
)


class PublicAuthMiddleware(BaseMiddleware):

    async def __call__(self, handler, event: Message | CallbackQuery, data):

        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
        else:
            return await handler(event, data)

        if not await is_saved_user(chat_id):
            await save_unauthorized_user(
                chat_id=chat_id,
                username=event.from_user.username,
                first_name=event.from_user.first_name,
                last_name=event.from_user.last_name,
            )
            return

        return await handler(event, data)


class PrivateAuthMiddlewareMessage(BaseMiddleware):

    async def __call__(self, handler, event: Message, data):

        if not await is_linked(event.chat.id):
            await event.answer("Сначала привяжите свой аккаунт", reply_markup=kb.link)
            return

        return await handler(event, data)


class PrivateAuthMiddlewareCallbackQuery(BaseMiddleware):

    async def __call__(self, handler, event: CallbackQuery, data):

        if not await is_linked(event.message.chat.id):
            await event.answer()
            await event.message.answer(
                "Сначала привяжите свой аккаунт", reply_markup=kb.link
            )
            return

        return await handler(event, data)
