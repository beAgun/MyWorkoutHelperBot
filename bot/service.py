from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.callbacks_types import TimeCB
import bot.keyboards as kb
from bot.constants import *
from bot.states import UserStates


class TimeInterface():

    @classmethod
    async def create_instance(cls, callback, callback_data, state):
        instance = cls(callback, callback_data, state)
        data = await state.get_data()
        instance.selected = data.get('NOTIFICATION_TIME_LIST', [])
        instance.custom_values = data.get('NOTIFICATION_TIME_CUSTOM_DICT', {})
        return instance

    def __init__(self, callback: CallbackQuery, callback_data: TimeCB, state: FSMContext):
        
        self.callback = callback
        self.state = state
            
        self.action = callback_data.action
        self.option_name = callback_data.option_name
        self.custom_idx = callback_data.custom_idx
        self.custom_action = callback_data.custom_action

        self.handlers = {
            'option': self._process_option,
            'custom': self._process_custom,
            'change_custom': self._process_change_custom,
            'confirm': self._process_confirm
        }
    
    async def process_time_callback_query(self):  

        await self.callback.answer()

        action, option_name, selected, callback = self.action, self.option_name, self.selected, self.callback

        if (((action == 'option' and option_name not in selected) or (action == 'custom')) 
        and len(selected) == TIME_OPTIONS_LIMIT):
            await callback.answer(f'Нельзя выбрать больше {TIME_OPTIONS_LIMIT} вариантов')
            return

        await self.handlers[action]()
    
    async def update_state(self):
        await self.state.update_data(NOTIFICATION_TIME_LIST=self.selected,
                                     NOTIFICATION_TIME_CUSTOM_DICT=self.custom_values)

    async def _process_custom(self):
        callback, state, selected, custom_values = self.callback, self.state, self.selected, self.custom_values
        # await callback.answer()
        new_custom = (len(custom_values) + 1)
        selected.append(new_custom)
        custom_values[new_custom] = {'value': 1, 'unit': 0}
        await state.update_data(NOTIFICATION_TIME_LIST=selected, 
                                NOTIFICATION_TIME_CUSTOM_DICT=custom_values)
        await callback.message.edit_reply_markup(
            reply_markup=kb.get_time_kb(selected, custom_values)
            )
        return

    async def _process_change_custom_plus(self):

        if self.custom_values[self.custom_idx]['value'] == CUSTOM_TIME_NUMBER_MAX:
            await self.callback.answer('Достигнуто максимальное значение')
            return
        
        await self.callback.answer()
        self.custom_values[self.custom_idx]['value'] += 1

    async def _process_change_custom_minus(self):

        if self.custom_values[self.custom_idx]['value'] == CUSTOM_TIME_NUMBER_MIN:
            await self.callback.answer('Достигнуто минимальное значение')
            return
        
        await self.callback.answer()
        self.custom_values[self.custom_idx]['value'] -= 1

    async def _process_change_custom_delete(self):

        await self.callback.answer('Время удалено')
        del self.custom_values[self.custom_idx]
        self.selected.remove(self.custom_idx)

    async def _process_change_custom_change_value(self):

        await self.callback.answer()
        await self.state.update_data(CUSTOM_TIME_KEY=self.custom_idx)
        await self.state.set_state(UserStates.CUSTOM_TIME_NUMBER)
        await self.callback.message.edit_text(f'Введите целое число от {CUSTOM_TIME_NUMBER_MIN} до {CUSTOM_TIME_NUMBER_MAX}')
        return

    async def _process_change_custom_change_unit(self):

        await self.callback.answer()
        self.custom_values[self.custom_idx]['unit'] += 1

    async def _process_change_custom(self):

        custom_handlers = {
            'plus': self._process_change_custom_plus,
            'minus': self._process_change_custom_minus,
            'delete': self._process_change_custom_delete,
            'change_value': self._process_change_custom_change_value,
            'change_unit': self._process_change_custom_change_unit,
        }

        await custom_handlers[self.custom_action]()

        if self.custom_action != 'change_value':
            await self.state.update_data(NOTIFICATION_TIME_CUSTOM_DICT=self.custom_values)
            await self.callback.message.edit_reply_markup(
                reply_markup=kb.get_time_kb(self.selected, self.custom_values)
            )
            return

    async def _process_option(self):
        callback, state, selected, custom_values = self.callback, self.state, self.selected, self.custom_values
        option_name = self.option_name
        await callback.answer()
        selected.remove(option_name) if option_name in selected else selected.append(option_name)
        await state.update_data(NOTIFICATION_TIME_LIST=selected)
        await callback.message.edit_reply_markup(reply_markup=kb.get_time_kb(selected, custom_values))

    async def _process_confirm(self):
        callback, state, selected, custom_values = self.callback, self.state, self.selected, self.custom_values
        if not selected:
            await callback.answer("Выберите хотя бы один вариант")
            return
        await callback.answer()
        await state.clear()

        content: list[str] = [
            (TimeOption._member_map_[s].value if not isinstance(s, int) else 
            f'за {custom_values[s]["value"]} {UNITS[custom_values[s]["unit"]%len(UNITS)].value}') 
            for s in selected
        ]
        await callback.message.edit_text(
            f"Вы выбрали: {', '.join(content)}",
            reply_markup=None
        )
    

async def choose_time_proccessor(callback: CallbackQuery, callback_data: TimeCB, state: FSMContext):
    
    data = await state.get_data()
    selected = data.get('NOTIFICATION_TIME_LIST', [])
    custom_values = data.get('NOTIFICATION_TIME_CUSTOM_DICT', {})
            
    action = callback_data.action
    option_name = callback_data.option_name
    custom_idx = callback_data.custom_idx
    custom_action = callback_data.custom_action

    if (((action == 'option' and option_name not in selected) or (action == 'custom')) 
    and len(selected) == TIME_OPTIONS_LIMIT):
        await callback.answer(f'Нельзя выбрать больше {TIME_OPTIONS_LIMIT} вариантов')
        return

    async def _process_custom():
        await callback.answer()
        new_custom = (len(custom_values) + 1)
        selected.append(new_custom)
        custom_values[new_custom] = {'value': 1, 'unit': 0}
        await state.update_data(NOTIFICATION_TIME_LIST=selected, 
                                NOTIFICATION_TIME_CUSTOM_DICT=custom_values)
        await callback.message.edit_reply_markup(
            reply_markup=kb.get_time_kb(selected, custom_values)
            )
        return

    async def _process_change_custom():
        custom_name, action = custom_idx, custom_action

        if action == 'plus':

            if custom_values[custom_name]['value'] == CUSTOM_TIME_NUMBER_MAX:
                await callback.answer('Достигнуто максимальное значение')
                return
            await callback.answer()
            custom_values[custom_name]['value'] += 1

        elif action == 'minus':

            if custom_values[custom_name]['value'] == CUSTOM_TIME_NUMBER_MIN:
                await callback.answer('Достигнуто минимальное значение')
                return
            await callback.answer()
            custom_values[custom_name]['value'] -= 1

        elif action == 'delete':

            await callback.answer('Время удалено')
            del custom_values[custom_name]
            selected.remove(custom_name)

        elif action == 'change_value':

            await callback.answer()
            await state.update_data(CUSTOM_TIME_KEY=custom_name)
            await state.set_state(UserStates.CUSTOM_TIME_NUMBER)
            await callback.message.edit_text(f'Введите целое число от {CUSTOM_TIME_NUMBER_MIN} до {CUSTOM_TIME_NUMBER_MAX}')
            return
        
        elif action == 'change_unit':

            await callback.answer()
            custom_values[custom_name]['unit'] += 1

        else:
            await callback.answer()

        await state.update_data(NOTIFICATION_TIME_CUSTOM_DICT=custom_values)
        await callback.message.edit_reply_markup(
            reply_markup=kb.get_time_kb(selected, custom_values)
        )
        return

    async def _process_option():
        await callback.answer()
        selected.remove(option_name) if option_name in selected else selected.append(option_name)
        await state.update_data(NOTIFICATION_TIME_LIST=selected)
        await callback.message.edit_reply_markup(reply_markup=kb.get_time_kb(selected, custom_values))

    async def _process_confirm():
        if not selected:
            await callback.answer("Выберите хотя бы один вариант")
            return
        await callback.answer()
        await state.clear()

        content: list[str] = [
            (TimeOption._member_map_[s].value if not s.startswith('CUSTOM') else 
            f'за {custom_values[s]["value"]} {UNITS[custom_values[s]["unit"]%len(UNITS)].value}') 
            for s in selected
        ]
        await callback.message.edit_text(
            f"Вы выбрали: {', '.join(content)}",
            reply_markup=None
        )

    handlers = {
        'option':_process_option,
        'custom':_process_custom,
        'change_custom':_process_change_custom,
        'confirm':_process_confirm
    }

    await callback.answer()
    await handlers[action]()
