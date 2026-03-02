from enum import Enum, auto


class TimeOption(Enum):
    EVENT = 'время события'
    MIN_10 = 'за 10 минут'
    HOUR_1 = 'за 1 час'
    DAY_1 = 'за сутки'
    CUSTOM = auto() # ???


class CustomTimeOptionUnit(Enum):
    minutes = 'мин.'
    hours = 'ч.'
    days = 'сут.'
    weeks = 'нед.'
    

TIME_OPTIONS = [TimeOption.EVENT, TimeOption.MIN_10, TimeOption.HOUR_1, TimeOption.DAY_1]
UNITS = list(CustomTimeOptionUnit)
TIME_OPTIONS_LIMIT = 5
CUSTOM_TIME_NUMBER_MIN = 0
CUSTOM_TIME_NUMBER_MAX = 120