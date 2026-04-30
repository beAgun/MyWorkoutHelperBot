from app.application.actions.notifications_settings_form import *
import asyncio
from pprint import pprint


class FakeFSMContext:
    def __init__(self):
        self.data = {}

    async def get_data(self):
        return self.data

    async def update_data(self, **kwargs):
        self.data.update(kwargs)


async def test_NotificationsSettingsForm():
    state = FakeFSMContext()
    f1 = await NotificationsSettingsForm.load(state=state)
    # print(f.notifications_settings)
    await f1.save()

    fake_cb_data = TimeCB(action="change_preset", option_key=1)
    f2 = await NotificationsSettingsForm.load(state=state)
    await f2.handle_action(cb_data=fake_cb_data, chat_id=1)
    await f2.save()
    pprint(f2.notifications_settings)
    pprint(state.data)


if __name__ == "__main__":
    asyncio.run(test_NotificationsSettingsForm())
