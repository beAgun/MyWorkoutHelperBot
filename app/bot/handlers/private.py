from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.bot.states import UserStates
import app.bot.keyboards as kb
from aiogram.fsm.context import FSMContext
from app.bot.callbacks_types import TimeCB
from app.domain.notifications.notification_time import NotificationsSettingsAction
from app.application.actions.notifications_settings_form import (
    NotificationsSettingsForm,
)
from config import settings
from app.bot.middlewares import (
    PrivateAuthMiddlewareMessage,
    PrivateAuthMiddlewareCallbackQuery,
    ErrorMiddleware,
)
from app.scheduler.scheduler import scheduler

private_router = Router()
private_router.message.middleware(ErrorMiddleware())
private_router.message.middleware(PrivateAuthMiddlewareMessage())
private_router.callback_query.middleware(ErrorMiddleware())
private_router.callback_query.middleware(PrivateAuthMiddlewareCallbackQuery())


@private_router.callback_query(F.data.startswith("notifications"))
async def notifications(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    action = callback.data
    form = await NotificationsSettingsForm.update(state, action=action)
    print(form.notifications_settings.action)
    if action == NotificationsSettingsAction.unsubscribe.code:
        await callback.message.edit_text(
            "Вы действительно хотите отписаться от всех уведомлений?",
            reply_markup=kb.claim_unsubscribe,
        )
        return
    await state.set_state(UserStates.NOTIFICATION_TYPE)
    await callback.message.edit_text(
        "Выберите тип уведомлений:", reply_markup=kb.notification_types
    )


@private_router.callback_query(F.data == "claim_unsubscribe")
async def claim_unsubscribe(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    form: NotificationsSettingsForm = await NotificationsSettingsForm.load(state)
    answer = await form.unsubscribe(chat_id=callback.from_user.id)
    await callback.message.edit_text(answer)


@private_router.callback_query(F.data == "edit_or_unsubscribe")
async def claim_unsubscribe(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        f"Привет, {callback.from_user.first_name}! Я telegram бот для уведомлений! Выбери действие:",
        reply_markup=kb.edit_or_unsubscribe,
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


def is_admin(chat_id: int):
    return chat_id in settings.ADMIN_IDS


@private_router.callback_query(F.data == "sport_event_pause_job")
async def get_notifications_times(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if is_admin(chat_id):
        job = scheduler.get_job("check_kgbrun_registration_open_job")
        if job.next_run_time is not None:
            scheduler.pause_job("check_kgbrun_registration_open_job")
            await callback.message.edit_text("Мониторинг остановлен")
        else:
            await callback.message.edit_text("Мониторинг уже остановлен")
    else:
        await callback.message.edit_text("У вас нет прав администратора")


@private_router.callback_query(F.data == "sport_event_resume_job")
async def get_notifications_times(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if is_admin(chat_id):
        job = scheduler.get_job("check_kgbrun_registration_open_job")
        if job.next_run_time is not None:
            await callback.message.edit_text("Мониторинг уже запущен")
        else:
            scheduler.resume_job("check_kgbrun_registration_open_job")
            await callback.message.edit_text("Мониторинг запущен")
    else:
        await callback.message.edit_text("У вас нет прав администратора")
