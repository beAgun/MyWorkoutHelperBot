from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from aiogram import Bot, Dispatcher
from bot_config import settings
from bot.handlers import router
from aiogram.types import Update
from bot.handlers import router
from bot_config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    app.state.bot = bot
    app.state.dp = dp

    await bot.set_webhook(settings.WEBHOOK_PATH)
    print("Webhook set")

    yield

    await bot.delete_webhook()
    await bot.session.close()
    print("Bot stopped")


app = FastAPI(lifespan=lifespan)


@app.post(settings.WEBHOOK_PATH)
async def webhook(request: Request):
    bot = request.app.state.bot
    dp = request.app.state.dp

    update = Update.model_validate(await request.json())
    await dp.feed_update(bot, update)

    return Response(status_code=200)


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8080, reload=False)

# async def main():
#     await dp.start_polling(bot)


# if __name__ == '__main__':
#     asyncio.run(main())
