from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
import uvicorn
from aiogram import Bot, Dispatcher
from config import settings
from app.bot.handlers import public_router, private_router
from aiogram.types import Update
from config import settings
from logger import logger
from app.services.utils import resolve_token
from tests.database import *
import sys
from app.db.database import session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.MODE == "TEST":
        await prepare_test_database()
    if "--seed" in sys.argv:
        async with session_manager() as session:
            await seed_test_data(session)

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(public_router)
    dp.include_router(private_router)

    app.state.bot = bot
    app.state.dp = dp

    await bot.set_webhook(settings.WEBHOOK_URL)
    yield
    await bot.delete_webhook()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.post(settings.WEBHOOK_PATH)
async def webhook(request: Request):
    try:
        bot = request.app.state.bot
        dp = request.app.state.dp

        update = Update.model_validate(await request.json())
        await dp.feed_update(bot, update)

        return Response(status_code=200)
    except Exception as e:
        logger.exception(e)
        return Response(status_code=200)


@app.get("/resolve-link-token")
async def resolve_link_token(token: str):
    await resolve_token(token)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)
