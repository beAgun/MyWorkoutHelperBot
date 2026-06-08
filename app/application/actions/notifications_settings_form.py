from aiogram.fsm.context import FSMContext
from app.bot.constants import *
from app.db.models_repo import *
from app.db.database import *
from app.bot.callbacks_types import TimeCB
from app.bot.states import *
import inspect
from logger import logger
from app.domain.notifications.notifications_settings import *
from app.application.actions.actions import *
from app.tasks.notifications import (
    create_user_notifications_task,
    delete_user_notifications_task,
    edit_user_notifications_task,
)


class NotificationsSettingsForm:
    def __init__(
        self, state: FSMContext, notifications_settings: NotificationsSettings
    ):
        self.state = state
        self.notifications_settings = notifications_settings

    @classmethod
    async def load(cls, state: FSMContext):
        data = await state.get_data()
        notifications_settings = data.get("notifications_settings")

        if notifications_settings is None:
            notifications_settings = NotificationsSettings()
            await state.update_data(notifications_settings=notifications_settings)

        return cls(state, notifications_settings)

    async def save(self):
        await self.state.update_data(notifications_settings=self.notifications_settings)

    @staticmethod
    async def update(state: FSMContext, **kwargs):
        form = await NotificationsSettingsForm.load(state)
        form.notifications_settings.update(**kwargs)
        await form.save()
        return form

    async def handle_action(self, cb_data: TimeCB, chat_id: int):
        action = Actions.get(cb_data.action)

        if action is None:
            raise ValueError(f"No action {cb_data.action}")

        result = action.execute(self, cb_data, chat_id)

        if inspect.isawaitable(result):
            return await result

        return result

    async def enter_custom_value(self, option_key: int) -> str:

        await self.state.update_data(custom_key=option_key)
        await self.state.set_state(UserStates.CUSTOM_VALUE)
        msg = f"Введите целое число от {MIN_TIME_VALUE} до {MAX_TIME_VALUE}"
        return msg

    async def confirm(self, chat_id: int) -> str:
        await self.state.clear()  # here?
        settings = self.notifications_settings
        chosen_times = settings.validate()

        if settings.action == NotificationsSettingsAction.subscribe.code:
            create_user_notifications_task.delay(
                [item.value_in_minutes for item in chosen_times], chat_id
            )
        elif settings.action == NotificationsSettingsAction.edit.code:
            edit_user_notifications_task.delay(
                [item.value_in_minutes for item in chosen_times], chat_id
            )

        msg = f"Вы выбрали: {', '.join([item.label for item in chosen_times])}"
        return msg

    async def unsubscribe(self, chat_id: int) -> str:
        await self.state.clear()

        delete_user_notifications_task.delay(chat_id)

        msg = "Вы отписались от уведомлений"
        return msg
