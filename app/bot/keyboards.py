from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.bot.constants import *
from app.bot.callbacks_types import *
from config import settings

BASE_CMDS = ["start", "link", "visit_site", "description"]


def get_main_rkb():
    rkb = ReplyKeyboardBuilder()
    for option in BASE_OPTIONS:
        rkb.add(KeyboardButton(**option))
    rkb.adjust(2).as_markup()
    return rkb


link = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Привязать аккаунт", callback_data="link")]
    ]
)

visit_site = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Посетить сайт", url="https://cursor.wbif.ru/")]
    ]
)


main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подписаться на уведомления", callback_data="notifications"
            )
        ]
    ]
)


notifications_types = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Тренировки", callback_data="trainings"),
            InlineKeyboardButton(text="Взвешивание", callback_data="weighting"),
        ]
    ]
)


trainings_types = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Все тренировки", callback_data="all_trainings")],
        [
            InlineKeyboardButton(
                text="Только с включёнными уведомлениями",
                callback_data="not_all_trainings",
            )
        ],
    ]
)


def get_time_kb(selected=None, custom_values=None, redraw_only: int = None):
    """
    Создаёт клавиатуру для выбора времени уведомлений.
    :param selected: список выбранных опций (str или int для кастомных)
    :param custom_values: словарь кастомных значений {1: {'value': 5, 'unit': 0}, ...}
    :param redraw_only: если указано, перерисовываем только эту кастомную кнопку
    """
    if selected is None:
        selected = []
    if custom_values is None:
        custom_values = {}

    kb = InlineKeyboardBuilder()

    for option in TIME_OPTIONS:
        postfix = " ✔️" if option.name in selected else ""
        kb.row(
            InlineKeyboardButton(
                text=f"{option.value}{postfix}", callback_data=cb_option(option.name)
            )
        )

    for custom_option in custom_values:
        value, unit_idx = (
            custom_values[custom_option]["value"],
            custom_values[custom_option]["unit"],
        )
        unit = UNITS[unit_idx % len(UNITS)].value
        kb.row(
            InlineKeyboardButton(
                text="➖", callback_data=cb_change_custom(custom_option, "minus")
            ),
            InlineKeyboardButton(
                text=f"{value}",
                callback_data=cb_change_custom(custom_option, "change_value"),
            ),
            InlineKeyboardButton(
                text="➕", callback_data=cb_change_custom(custom_option, "plus")
            ),
            InlineKeyboardButton(
                text=f"{unit}",
                callback_data=cb_change_custom(custom_option, "change_unit"),
            ),
            InlineKeyboardButton(
                text="🗑", callback_data=cb_change_custom(custom_option, "delete")
            ),
        )

    if len(selected) < TIME_OPTIONS_LIMIT:
        kb.row(InlineKeyboardButton(text="Произвольное ➕", callback_data=cb_custom()))

    kb.row(InlineKeyboardButton(text="Подтвердить ✔️", callback_data=cb_confirm()))

    return kb.as_markup()
