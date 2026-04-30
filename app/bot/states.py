from aiogram.fsm.state import State, StatesGroup


class LinkUserStates(StatesGroup):
    EMAIL = State()
    EMAIL_ATTEMPTS = State()


class UserStates(StatesGroup):
    NOTIFICATION_TYPE = State()
    TRAININGS_NOTIFICATION_TYPE = State()
    NOTIFICATIONS_TIMES = State()

    CUSTOM_KEY = State()
    CUSTOM_VALUE = State()
