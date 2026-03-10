from aiogram.filters.callback_data import CallbackData


class TimeCB(CallbackData, prefix='time'):
    action: str # option, custom, change_custom, confirm
    option_name: str | None = None # TimeOption
    custom_idx: int | None = None
    custom_action: str | None = None # delete, minus, plus, change_unit, change_value


cb_option = lambda name: TimeCB(action='option', option_name=name).pack() #time:change_custom:1:delete
cb_custom = lambda: TimeCB(action='custom').pack()
cb_change_custom = lambda idx, action: TimeCB(action='change_custom', custom_idx=idx, custom_action=action).pack()
cb_confirm = lambda: TimeCB(action='confirm').pack()

