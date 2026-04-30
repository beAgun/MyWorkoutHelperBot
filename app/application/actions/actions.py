from dataclasses import dataclass
from typing import Any
from app.bot.callbacks_types import TimeCB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.actions.notifications_settings_form import (
        NotificationsSettingsForm,
    )


# BaseAction, BaseStateAction, BaseCallbackAction
@dataclass(frozen=True)
class BaseAction:
    name: str

    def execute(self, form: "NotificationsSettingsForm", data: TimeCB, chat_id: int):
        raise NotImplementedError

    def cb_data(self, **kwargs) -> str:
        return TimeCB(action=self.name, **kwargs).pack()


class NoParamsAction(BaseAction):

    def execute(self, form: "NotificationsSettingsForm", data: TimeCB, chat_id: int):
        handler = getattr(form.notifications_settings, self.name)
        return handler()

    def cb_data(self) -> str:
        return super().cb_data()


class KeyAction(BaseAction):

    def execute(self, form: "NotificationsSettingsForm", data: TimeCB, chat_id: int):
        handler = getattr(form.notifications_settings, self.name)
        return handler(data.option_key)

    def cb_data(self, option_key: int) -> str:
        return super().cb_data(option_key=option_key)


class KeyValueAction(BaseAction):
    def execute(self, form: "NotificationsSettingsForm", data: TimeCB, chat_id: int):
        handler = getattr(form.notifications_settings, self.name)
        return handler(data.option_key, data.value)

    def cb_data(self, option_key: int, value: Any) -> str:
        return super().cb_data(option_key=option_key, value=value)


class EnterCustomValueAction(BaseAction):
    def execute(self, form: "NotificationsSettingsForm", data: TimeCB, chat_id: int):
        return form.enter_custom_value(option_key=data.option_key)

    def cb_data(self, option_key: int) -> str:
        return super().cb_data(option_key=option_key)


class ConfirmAction(BaseAction):
    def execute(self, form: "NotificationsSettingsForm", data: TimeCB, chat_id: int):
        return form.confirm(chat_id=chat_id)

    def cb_data(self) -> str:
        return super().cb_data()


class Actions:
    change_preset = KeyAction("change_preset")
    add_custom = NoParamsAction("add_custom")
    minus_custom_value = KeyAction("minus_custom_value")
    plus_custom_value = KeyAction("plus_custom_value")
    enter_custom_value = EnterCustomValueAction("enter_custom_value")
    change_custom_value = KeyValueAction("change_custom_value")
    change_custom_unit = KeyAction("change_custom_unit")
    delete_custom = KeyAction("delete_custom")
    confirm = ConfirmAction("confirm")

    @classmethod
    def get(cls, action_name: str) -> BaseAction:
        action = getattr(cls, action_name, None)

        if not isinstance(action, BaseAction):
            raise ValueError(f"Invalid action {action_name}")

        return action
