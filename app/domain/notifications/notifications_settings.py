from dataclasses import dataclass, field
from app.bot.constants import *
from .notification_time import *
from .notifications_times_list import *


@dataclass
class NotificationsSettings:
    notification_type: NotificationType = None
    trainings_notification_type: TrainingsNotificationType = None
    notifications_times: NotificationsTimesList = field(
        default_factory=lambda: NotificationsSettings.set_preset_times()
    )

    @staticmethod
    def set_preset_times():
        preset_times = NotificationsTimesList(
            [
                NotificationTime(
                    value=0, unit=TimeUnit.minute, label="время события", is_preset=True
                ),
                NotificationTime(
                    value=10, unit=TimeUnit.minute, label="за 10 минут", is_preset=True
                ),
                NotificationTime(
                    value=1, unit=TimeUnit.hour, label="за час", is_preset=True
                ),
                NotificationTime(
                    value=1, unit=TimeUnit.day, label="за сутки", is_preset=True
                ),
            ]
        )
        return preset_times

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Unknown field: {key}")
            setattr(self, key, value)

    def validate(self) -> list[NotificationTime]:
        """
        Validates list of notifications times and returns list of unique chosen times
        returns: list of unique chosen times
        """
        chosen_times = [item for item in self.notifications_times if item.chosen]

        if not chosen_times:
            raise ValueError("Хотя бы один вариант должен быть выбран")

        if len(chosen_times) > TIME_OPTIONS_LIMIT:
            raise ValueError(f"Нельзя выбрать больше {TIME_OPTIONS_LIMIT} вариантов")

        return sorted(list(set(chosen_times)), key=lambda x: x.value_in_minutes)

    def change_preset(self, option_key: int):
        _, time = self.notifications_times.get_by_key(option_key)
        self.notifications_times.replace_by_key(option_key, chosen=not time.chosen)

    def add_custom(self):
        chosen_times_in_minutes = [
            item.value_in_minutes for item in self.notifications_times if item.chosen
        ]
        new_custom_value = 1
        while new_custom_value in chosen_times_in_minutes:
            new_custom_value += 1
        default_custom_time = NotificationTime(
            value=new_custom_value, unit=TimeUnit.minute, chosen=True
        )
        self.notifications_times.append(default_custom_time)

    def minus_custom_value(self, option_key: int):
        _, time = self.notifications_times.get_by_key(option_key)
        self.notifications_times.replace_by_key(option_key, value=time.value - 1)

    def plus_custom_value(self, option_key: int):
        _, time = self.notifications_times.get_by_key(option_key)
        self.notifications_times.replace_by_key(option_key, value=time.value + 1)

    def change_custom_value(self, option_key: int, value: int):
        self.notifications_times.replace_by_key(option_key, value=value)

    def change_custom_unit(self, option_key: int):
        _, time = self.notifications_times.get_by_key(option_key)
        self.notifications_times.replace_by_key(option_key, unit=time.unit.next())

    def delete_custom(self, option_key: int):
        self.notifications_times.delete_by_key(option_key)
