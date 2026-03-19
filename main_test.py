import asyncio
from aiogram import Bot, Dispatcher
from config import settings
from app.bot.handlers import public_router, private_router
from config import settings
import sys
import warnings
from tests.database import *
from app.db.database import session_manager


async def main():

    if settings.MODE == "TEST":
        await prepare_test_database()
    if "--seed" in sys.argv:
        async with session_manager() as session:
            await seed_test_data(session)

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(public_router)
    dp.include_router(private_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    warnings.filterwarnings(
        "ignore", category=RuntimeWarning, message="Event loop is closed"
    )
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError) as e:
        sys.exit()
