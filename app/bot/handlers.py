from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command, CommandObject
from app.bot.states import UserStates, LinkUserStates
import app.bot.keyboards as kb
from aiogram.fsm.context import FSMContext
from app.bot.constants import *
from app.bot.callbacks_types import *
from app.services.service import TimeInterface
from app.services.utils import handle_linking, validate_user_email
from config import settings
from app.bot.middlewares import is_linked


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()

    token = command.args

    if token:
        text = await handle_linking(message, token)
        kbd = kb.get_main_rkb()
    else:
        if not await is_linked(message.from_user.id):
            text = (
                "Я telegram бот для уведомлений! "
                "Чтобы продолжить, привяжи аккаунт на сайте MyWorkoutTracker."
            )
            kbd = kb.link
        else:
            text = "Я telegram бот для уведомлений! Выбери действие:"
            kbd = kb.main

    await message.answer(
        f"Привет, {message.from_user.first_name}! {text}",
        reply_markup=kbd,
    )


async def start_linking(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(LinkUserStates.EMAIL)
    await message.answer(
        text=f"Введите адрес почты, с которой регистрировались на сайте"
    )


@router.callback_query(LinkUserStates.EMAIL)
async def trainings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    validated_email = validate_user_email(email=callback.data)
    if validated_email is None:
        await state.set_state(LinkUserStates.EMAIL)
        await callback.answer(
            text=f"Формат адреса почты неверный. Введите заново", show_alert=True
        )
        return

    # site_request_for_email(email=validated_email)
    await state.set_data(LinkUserStates.LINK_CODE)
    await callback.message.answer(
        text="На указанный почтовый адрес придёт сообщение с кодом из 6 цифр. Введите его",
    )


@router.message(Command("link"))
async def cmd_link(message: Message, state: FSMContext):
    await start_linking(message, state)


@router.callback_query(F.data == "link")
async def cb_link(callback: CallbackQuery, state: FSMContext):
    await start_linking(callback.message, state)


@router.message(Command("description"))
async def cmd_description(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=(
            f"Бот MyWorkoutHelper поможет настроить уведомления о предстоящих "
            "тренировках, спортивных мероприятиях, которые ты добавишь в своём "
            "дневнике тренировок на сайте MyWorkoutTracker. Также можно настроить "
            "уведомления о периодическом взвешивании."
        ),
        reply_markup=kb.main,
    )


@router.message(Command("visit_site"))
async def cmd_visit_site(message: Message):
    await message.answer(f"Добро пожаловать!", reply_markup=kb.visit_site)


@router.callback_query(F.data == "notifications")
async def notifications(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(UserStates.NOTIFICATION_TYPE)
    await callback.message.edit_text(
        "Выберите тип уведомлений:", reply_markup=kb.notifications_types
    )


@router.callback_query(UserStates.NOTIFICATION_TYPE)
async def trainings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(NOTIFICATION_TYPE=callback.data)
    await state.set_state(UserStates.TRAININGS_NOTIFICATION_TYPE)
    await callback.message.edit_text(
        "Уведомлять о всех тренировках или "
        "только о тренировках, у которых включены уведомления на сайте?",
        reply_markup=kb.trainings_types,
    )


@router.callback_query(UserStates.TRAININGS_NOTIFICATION_TYPE)
async def time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(TRAININGS_NOTIFICATION_TYPE=callback.data)
    await state.set_state(UserStates.NOTIFICATION_TIME_LIST)
    await callback.message.edit_text(
        "Выберите время уведомлений", reply_markup=kb.get_time_kb()
    )


@router.callback_query(TimeCB.filter())
async def choose_time(
    callback: CallbackQuery, callback_data: TimeCB, state: FSMContext
):

    ins = await TimeInterface.create_instance(callback, callback_data, state)
    await ins.process_time_callback_query()
    # await choose_time_proccessor(callback, callback_data, state)


@router.message(UserStates.CUSTOM_TIME_NUMBER)
async def number_entered(message: Message, state: FSMContext):
    text = message.text.strip()

    if not text.isdigit():
        await message.answer("Введите целое число")
        return

    value = int(text)

    if not (CUSTOM_TIME_NUMBER_MIN <= value <= CUSTOM_TIME_NUMBER_MAX):
        await message.answer(
            f"Диапазон {CUSTOM_TIME_NUMBER_MIN} – {CUSTOM_TIME_NUMBER_MAX}"
        )
        return

    data = await state.get_data()

    selected = data.get("NOTIFICATION_TIME_LIST", [])
    custom_values = data.get("NOTIFICATION_TIME_CUSTOM_DICT")  # !None
    custom_name = data.get("CUSTOM_TIME_KEY")
    custom_values[custom_name]["value"] = value

    await state.update_data(NOTIFICATION_TIME_CUSTOM_DICT=custom_values)

    await state.set_state(UserStates.NOTIFICATION_TIME_LIST)
    await message.answer(
        "Выберите время уведомлений",
        reply_markup=kb.get_time_kb(selected, custom_values),
    )
