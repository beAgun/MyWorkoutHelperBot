from dataclasses import replace
from typing import Tuple
from app.bot.constants import *
from .notification_time import NotificationTime


class NotificationsTimesList(list[NotificationTime]):
    def __init__(self, iterable: list[NotificationTime] = None):
        super().__init__()

        self._key_counter = 0

        if iterable:
            for item in iterable:
                self.append(item)

    def validate(self, obj: NotificationTime):  # not used
        if (
            sum(item.chosen for item in self) + (1 if obj.chosen else 0)
            > TIME_OPTIONS_LIMIT
        ):
            raise ValueError(f"Нельзя выбрать больше {TIME_OPTIONS_LIMIT} вариантов")

        if obj.chosen and any(
            item.value_in_minutes == obj.value_in_minutes
            for item in self
            if item.chosen
        ):
            raise ValueError(f'Вариант "{obj.label}" уже выбран')

    def append(self, obj: NotificationTime):
        obj = replace(obj)  # TODO
        # self.validate(obj)
        self._key_counter += 1
        object.__setattr__(obj, "key", self._key_counter)
        return super().append(obj)

    def get_by_key(self, key: int) -> Tuple[int, NotificationTime]:
        for i, item in enumerate(self):
            if item.key == key:
                return i, item
        raise ValueError("Element was not found")

    def replace_by_key(self, key: int, **kwargs):
        idx, item = self.get_by_key(key)
        new = replace(item, **kwargs)
        object.__setattr__(new, "key", item.key)
        if not new.is_preset:
            object.__setattr__(new, "label", new._generate_label())
        # self.validate(new)
        self[idx] = new
        return new

    def delete_by_key(self, key: int):
        idx, _ = self.get_by_key(key)
        del self[idx]
