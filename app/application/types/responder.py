from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app.db.models import *
from app.application.types.response import Response


class Responder:
    async def send(
        self, callback: CallbackQuery, state: FSMContext, response: Response
    ):

        # 1. alert (callback.answer)
        if response.alert is not None:
            await callback.answer(response.alert)
        else:
            await callback.answer()

        # 2. state
        if response.state_data:
            await state.update_data(**response.state_data)

        if response.new_state:
            await state.set_state(response.new_state)

        # 3. message updates
        if response.edit_text:
            await callback.message.edit_text(
                text=response.text, reply_markup=response.keyboard
            )
        elif response.edit_markup:
            await callback.message.edit_reply_markup(reply_markup=response.keyboard)
        elif response.text:
            await callback.message.answer(
                text=response.text, reply_markup=response.keyboard
            )
