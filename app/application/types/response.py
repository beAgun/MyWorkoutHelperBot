from aiogram.types import InlineKeyboardMarkup
from app.db.models import *
from dataclasses import dataclass
from aiogram.types import InlineKeyboardMarkup


@dataclass
class Response:
    text: str | None = None
    keyboard: InlineKeyboardMarkup | None = None

    edit_text: bool = False
    edit_markup: bool = False

    alert: str | None = None

    new_state: any = None
    state_data: dict | None = None
