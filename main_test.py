import asyncio
from aiogram import Bot, Dispatcher
from config import settings
from app.bot.handlers import router
from app.bot.handlers import router
from config import settings
import sys
import warnings
from tests.database import prepare_test_database, seed_test_data
from app.db.database import session_manager


async def main():

    if settings.MODE == "TEST" and "--seed" in sys.argv:
        await prepare_test_database()
        async with session_manager() as session:
            await seed_test_data(session)

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    warnings.filterwarnings(
        "ignore", category=RuntimeWarning, message="Event loop is closed"
    )
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError) as e:
        sys.exit()
