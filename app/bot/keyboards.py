from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import settings
from app.domain.notifications.notifications_settings import *
from app.application.actions.actions import Actions

BASE_CMDS = ["start", "link", "visit_site", "description"]


link = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Привязать аккаунт", callback_data="link")]
    ]
)

visit_site = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Посетить сайт", url=settings.WORKOUT_SITE_LINK)]
    ]
)


subscribe = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=NotificationsSettingsAction.subscribe.label,
                callback_data=NotificationsSettingsAction.subscribe.code,
            )
        ]
    ]
)


edit_or_unsubscribe = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=NotificationsSettingsAction.edit.label,
                callback_data=NotificationsSettingsAction.edit.code,
            )
        ],
        [
            InlineKeyboardButton(
                text=NotificationsSettingsAction.unsubscribe.label,
                callback_data=NotificationsSettingsAction.unsubscribe.code,
            )
        ],
    ]
)


claim_unsubscribe = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подтвердить удаление", callback_data="claim_unsubscribe"
            )
        ],
        [
            InlineKeyboardButton(
                text="Вернуться назад", callback_data="edit_or_unsubscribe"
            )
        ],
    ]
)


notification_types = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=item.label, callback_data=item.code)
            for item in NotificationType
        ]
    ]
)


trainings_notification_types = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=item.label, callback_data=item.code)]
        for item in TrainingsNotificationType
    ]
)


def get_time_kb(notifications_times: NotificationsTimesList):
    """
    Создаёт клавиатуру для выбора времени уведомлений.
    :param notifications_times: список опций
    """
    kb = InlineKeyboardBuilder()
    # notifications_times.sort(key=lambda time: time.is_preset)

    for option in notifications_times:
        if option.is_preset:
            postfix = " ✔️" if option.chosen else ""
            kb.row(
                InlineKeyboardButton(
                    text=f"{option.label}{postfix}",
                    callback_data=Actions.change_preset.cb_data(option.key),
                )
            )
        else:
            kb.row(
                InlineKeyboardButton(
                    text="➖",
                    callback_data=Actions.minus_custom_value.cb_data(option.key),
                ),
                InlineKeyboardButton(
                    text=f"{option.value}",
                    callback_data=Actions.enter_custom_value.cb_data(option.key),
                ),
                InlineKeyboardButton(
                    text="➕",
                    callback_data=Actions.plus_custom_value.cb_data(option.key),
                ),
                InlineKeyboardButton(
                    text=f"{option.unit.label}",
                    callback_data=Actions.change_custom_unit.cb_data(option.key),
                ),
                InlineKeyboardButton(
                    text="🗑",
                    callback_data=Actions.delete_custom.cb_data(option.key),
                ),
            )

    if sum(item.chosen for item in notifications_times) < TIME_OPTIONS_LIMIT:
        kb.row(
            InlineKeyboardButton(
                text="Произвольное ➕", callback_data=Actions.add_custom.cb_data()
            )
        )

    kb.row(
        InlineKeyboardButton(
            text="Подтвердить ✔️", callback_data=Actions.confirm.cb_data()
        )
    )

    return kb.as_markup()
