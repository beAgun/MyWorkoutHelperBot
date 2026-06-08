from aiogram.filters.callback_data import CallbackData
from typing import Any


class TimeCB(CallbackData, prefix="time"):
    action: str
    option_key: int | None = None
    value: Any | None = None
