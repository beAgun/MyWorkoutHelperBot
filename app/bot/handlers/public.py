from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from app.bot.states import LinkUserStates
import app.bot.keyboards as kb
from aiogram.fsm.context import FSMContext
from app.bot.middlewares import PublicAuthMiddleware
from config import settings
from app.application.user.email_service import request_email_link
from app.application.security.rate_limit import check_attempts
from app.application.user.linking_service import handle_linking
from app.application.user.repository import is_linked, user_has_notifications_enabled
from sqlalchemy.exc import IntegrityError

public_router = Router()
public_router.message.middleware(PublicAuthMiddleware())
public_router.callback_query.middleware(PublicAuthMiddleware())


@public_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()

    token = command.args

    if token:
        try:
            text = await handle_linking(message, token)
            text += " Выбери действие:"
            kbd = kb.subscribe
        except ValueError as err:
            text = str(err)
            kbd = None
        except IntegrityError as err:
            text = str(err)
            text += " Перепривязать аккаунт?"
            kbd = kb.link
    else:
        site_user_id = await is_linked(message.chat.id)
        if site_user_id is None:
            text = (
                "Я telegram бот для уведомлений! "
                "Чтобы продолжить, привяжи аккаунт на сайте MyWorkoutTracker."
            )
            kbd = kb.link
        else:
            text = "Я telegram бот для уведомлений! Выбери действие:"
            if await user_has_notifications_enabled(site_user_id):
                kbd = kb.edit_or_unsubscribe
            else:
                kbd = kb.subscribe

    await message.answer(
        f"Привет, {message.from_user.first_name}! {text}",
        reply_markup=kbd,
    )


@public_router.message(Command("link"))
async def cmd_link(message: Message, state: FSMContext):
    await start_linking(message, state)


@public_router.callback_query(F.data == "link")
async def cb_link(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_linking(callback.message, state)


async def start_linking(message: Message, state: FSMContext):
    await state.clear()
    if await is_linked(message.chat.id):
        await message.answer(text=f"Telegram аккаунт уже привязан к аккаунту на сайте")
    else:
        await state.set_state(LinkUserStates.EMAIL)
        await message.answer(
            text=f"Введите адрес почты, с которой регистрировались на сайте"
        )


@public_router.message(LinkUserStates.EMAIL)
async def email_handler(message: Message, state: FSMContext):
    if not await check_attempts(state, "EMAIL_ATTEMPTS"):
        await state.clear()
        await message.answer("Слишком много попыток. Попробуйте начать сначала")
        return

    try:
        msg = await request_email_link(email=message.text, chat_id=message.chat.id)
        await state.clear()
        await message.answer(text=msg)
    except ValueError as err:
        await state.set_state(LinkUserStates.EMAIL)
        await message.answer(text=str(err))


@public_router.message(Command("description"))
async def cmd_description(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=(
            f"Бот MyWorkoutHelper поможет настроить уведомления о предстоящих "
            "тренировках, спортивных мероприятиях, которые ты добавишь в своём "
            "дневнике тренировок на сайте MyWorkoutTracker. Также можно настроить "
            "уведомления о периодическом взвешивании."
        ),
    )


@public_router.message(Command("visit_site"))
async def cmd_visit_site(message: Message):
    await message.answer(f"Добро пожаловать!", reply_markup=kb.visit_site)
