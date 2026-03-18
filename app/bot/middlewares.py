from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import app.bot.keyboards as kb
from app.db.models_repo import *
from app.db.database import session_manager


async def is_linked(user_id: int):
    async with session_manager() as session:
        user = await UserRepo.get_row_by_id(
            session=session, model_id=user_id
        )  # TODO: get_user_by_chat_id
        return user


class AuthMiddlewareMessage(BaseMiddleware):

    async def __call__(self, handler, event: Message, data):

        if (cmd := data.get("command")) and cmd.command in kb.BASE_CMDS:
            return await handler(event, data)

        if not await is_linked(event.from_user.id):
            await event.answer("Сначала привяжите свой аккаунт", reply_markup=kb.link)
            return

        return await handler(event, data)


class AuthMiddlewareCallbackQuery(BaseMiddleware):

    async def __call__(self, handler, event: CallbackQuery, data):

        if event.data in kb.BASE_CMDS:
            return await handler(event, data)

        if not await is_linked(event.from_user.id):
            await event.answer()
            await event.message.answer(
                "Сначала привяжите свой аккаунт", reply_markup=kb.link
            )
            return

        return await handler(event, data)
