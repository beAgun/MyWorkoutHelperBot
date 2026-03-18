from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class LinkUserStates(StatesGroup):
    EMAIL = State()
    LINK_CODE = State()


class UserStates(StatesGroup):
    START = State()
    SUBSCRIBE = State()
    NOTIFICATION_TYPE = State()
    TRAININGS_NOTIFICATION_TYPE = State()
    NOTIFICATION_TIME_LIST = State()
    NOTIFICATION_TIME_CUSTOM_DICT = State()
    CUSTOM_TIME_KEY = State()
    CUSTOM_TIME_NUMBER = State()
    CONFIRM = State()
