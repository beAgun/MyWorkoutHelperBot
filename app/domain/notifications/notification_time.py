from dataclasses import dataclass, field
from enum import Enum
from app.bot.constants import *


class LabeledEnum(Enum):
    def __init__(self, code, label):
        self.code = code
        self.label = label

    @classmethod
    def from_code(cls, code: str):
        return next(item for item in cls if item.code == code)


class NotificationsSettingsAction(LabeledEnum):
    subscribe = "notifications.subscribe", "Подписаться на уведомления"
    edit = "notifications.edit", "Настроить уведомления"
    unsubscribe = "notifications.unsubscribe", "Отписаться от уведомлений"


class NotificationType(LabeledEnum):
    # weighting = "weighting", "взвешивание"
    trainings = "trainings", "тренировки"


class TrainingsNotificationType(LabeledEnum):
    all = "all", "все тренировки"
    # only_enabled = "only_enabled", "только с включёнными уведомлениями"
    # certain = "certain", "определённая тренировка"


class TimeUnit(LabeledEnum):
    minute = 0, "мин."
    hour = 1, "ч."
    day = 2, "сут."

    @property
    def minutes(self) -> int:
        if self.name == "minute":
            return 1
        elif self.name == "hour":
            return 60
        elif self.name == "day":
            return 60 * 24

    def next(self):
        members = list(type(self))
        idx = members.index(self)
        return members[(idx + 1) % len(members)]


@dataclass(frozen=True)
class NotificationTime:
    value: int  # 0 120
    unit: TimeUnit
    label: str | None = None
    is_preset: bool = False
    chosen: bool = False

    key: int = field(init=False, default=-1)

    def __post_init__(self):
        object.__setattr__(self, "label", self.label or self._generate_label())
        self.validate()

    def validate(self):
        if not isinstance(self.value, int):
            try:
                object.__setattr__(self, "value", int(self.value))
            except ValueError:
                raise ValueError("Значение должно быть целым числом")
        if not (MIN_TIME_VALUE <= self.value <= MAX_TIME_VALUE):
            raise ValueError(f"Допустимый диапазон {MIN_TIME_VALUE} - {MAX_TIME_VALUE}")

    def _generate_label(self) -> str:
        return f"за {self.value} {self.unit.label}"

    def __eq__(self, value: "NotificationTime"):
        return self.value_in_minutes == value.value_in_minutes

    def __hash__(self):
        return hash(self.value_in_minutes)

    @property
    def value_in_minutes(self) -> int:
        return self.value * self.unit.minutes
