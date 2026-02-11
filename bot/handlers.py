from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from bot.states import UserStates
import bot.keyboards as kb
from aiogram.fsm.context import FSMContext
from bot.constants import *
from bot.callbacks_types import *
from bot.service import TimeInterface, choose_time_proccessor


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    # await message.reply(text='...', reply_markup=kb.start)
    await message.answer(
        f"Привет, {message.from_user.first_name}! Выбери действие:", 
        reply_markup=kb.main,
    )


@router.callback_query(F.data == 'notifications')
async def notifications(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(UserStates.NOTIFICATION_TYPE)
    await callback.message.edit_text('Выберите тип уведомлений:', reply_markup=kb.notifications_types)


@router.callback_query(UserStates.NOTIFICATION_TYPE)
async def trainings(callback: CallbackQuery, state: FSMContext):
    print(callback.chat_instance)
    await callback.answer()
    await state.update_data(NOTIFICATION_TYPE=callback.data)
    await state.set_state(UserStates.TRAININGS_NOTIFICATION_TYPE)
    await callback.message.edit_text('Уведомлять о всех тренировках или ' \
    'только о тренировках, у которых включены уведомления на сайте?',
    reply_markup=kb.trainings_types
    )


@router.callback_query(UserStates.TRAININGS_NOTIFICATION_TYPE)
async def time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(TRAININGS_NOTIFICATION_TYPE=callback.data)
    await state.set_state(UserStates.NOTIFICATION_TIME_LIST)
    await callback.message.edit_text('Выберите время уведомлений', 
                                     reply_markup=kb.get_time_kb())


@router.callback_query(TimeCB.filter())
async def choose_time(callback: CallbackQuery, callback_data: TimeCB, state: FSMContext):
    
    ins = await TimeInterface.create_instance(callback, callback_data, state)
    await ins.process_time_callback_query()
    # await choose_time_proccessor(callback, callback_data, state)
    

@router.message(UserStates.CUSTOM_TIME_NUMBER)
async def number_entered(message: Message, state: FSMContext):
    text = message.text.strip()

    if not text.isdigit():
        await message.answer('Введите целое число')
        return

    value = int(text)

    if not (CUSTOM_TIME_NUMBER_MIN <= value <= CUSTOM_TIME_NUMBER_MAX):
        await message.answer(f'Диапазон {CUSTOM_TIME_NUMBER_MIN} – {CUSTOM_TIME_NUMBER_MAX}')
        return

    data = await state.get_data()

    selected = data.get('NOTIFICATION_TIME_LIST', [])
    custom_values = data.get('NOTIFICATION_TIME_CUSTOM_DICT') # !None
    custom_name = data.get('CUSTOM_TIME_KEY')
    custom_values[custom_name]['value'] = value

    await state.update_data(NOTIFICATION_TIME_CUSTOM_DICT=custom_values)

    await state.set_state(UserStates.NOTIFICATION_TIME_LIST)
    await message.answer('Выберите время уведомлений', 
                         reply_markup=kb.get_time_kb(selected, custom_values))
