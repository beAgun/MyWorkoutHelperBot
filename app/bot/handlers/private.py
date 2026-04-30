from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.bot.states import UserStates
import app.bot.keyboards as kb
from aiogram.fsm.context import FSMContext
from app.bot.callbacks_types import TimeCB
from app.application.actions.notifications_settings_form import (
    NotificationsSettingsForm,
)
from config import settings
from app.bot.middlewares import (
    PrivateAuthMiddlewareMessage,
    PrivateAuthMiddlewareCallbackQuery,
)


private_router = Router()
private_router.message.middleware(PrivateAuthMiddlewareMessage())
private_router.callback_query.middleware(PrivateAuthMiddlewareCallbackQuery())


@private_router.callback_query(F.data == "notifications")
async def notifications(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(UserStates.NOTIFICATION_TYPE)
    await callback.message.edit_text(
        "Выберите тип уведомлений:", reply_markup=kb.notification_types
    )


@private_router.callback_query(UserStates.NOTIFICATION_TYPE)
async def get_notification_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await NotificationsSettingsForm.update(state, notification_type=callback.data)
    await state.set_state(
        UserStates.TRAININGS_NOTIFICATION_TYPE
    )  # TODO: weighting vs trainings
    await callback.message.edit_text(
        "На какие тренировки настроить уведомления?",
        reply_markup=kb.trainings_notification_types,
    )


@private_router.callback_query(UserStates.TRAININGS_NOTIFICATION_TYPE)
async def get_trainings_notification_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    form = await NotificationsSettingsForm.update(
        state, trainings_notification_type=callback.data
    )
    await state.set_state(UserStates.NOTIFICATIONS_TIMES)
    await callback.message.edit_text(
        "Выберите время уведомлений",
        reply_markup=kb.get_time_kb(form.notifications_settings.notifications_times),
    )


@private_router.callback_query(TimeCB.filter())
async def get_notifications_times(
    callback: CallbackQuery, callback_data: TimeCB, state: FSMContext
):
    try:
        form: NotificationsSettingsForm = await NotificationsSettingsForm.load(state)
        res = await form.handle_action(
            cb_data=callback_data, chat_id=callback.from_user.id
        )
        await form.save()
        await callback.answer()
        if res is not None and isinstance(res, str):
            await callback.message.edit_text(text=res, reply_markup=None)
        else:
            await callback.message.edit_reply_markup(
                reply_markup=kb.get_time_kb(
                    notifications_times=form.notifications_settings.notifications_times
                )
            )
    except ValueError as err:
        await callback.answer(text=str(err), show_alert=True)


@private_router.message(UserStates.CUSTOM_VALUE)
async def get_custom_time_value(message: Message, state: FSMContext):

    data = await state.get_data()
    custom_key = data.get("custom_key")
    custom_value = message.text.strip()
    try:
        form: NotificationsSettingsForm = await NotificationsSettingsForm.load(state)
        cb = TimeCB(
            action="change_custom_value", option_key=custom_key, value=custom_value
        )
        await form.handle_action(cb_data=cb, chat_id=message.chat.id)
        await form.save()
        await state.set_state(UserStates.NOTIFICATIONS_TIMES)
        await message.answer(
            "Выберите время уведомлений",
            reply_markup=kb.get_time_kb(
                notifications_times=form.notifications_settings.notifications_times
            ),
        )
    except ValueError as err:
        await message.answer(text=str(err), show_alert=True)
