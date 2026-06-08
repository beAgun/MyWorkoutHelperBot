from aiogram.fsm.context import FSMContext


async def check_attempts(
    state: FSMContext, key: str = "ATTEMPTS", max_attempts: int = 5
) -> bool:

    data = await state.get_data()
    attempts = data.get(key, 0)

    if attempts >= max_attempts:
        return False

    await state.update_data(**{key: attempts + 1})
    return True
