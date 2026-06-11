from fastapi import FastAPI, Request, Response, APIRouter
from contextlib import asynccontextmanager
import uvicorn
from aiogram import Bot, Dispatcher
from config import settings
from app.bot.handlers.public import public_router
from app.bot.handlers.private import private_router
from aiogram.types import Update
from config import settings
from logger import logger
from app.utils import resolve_token, confirm_relink
from tests.database import prepare_test_database, seed_test_data
import sys
from app.db.database import session_manager
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector
from app.scheduler.scheduler import scheduler_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.MODE == "TEST":
        await prepare_test_database()
    if "--seed" in sys.argv:
        async with session_manager() as session:
            await seed_test_data(session)

    # session = AiohttpSession(proxy="socks5://127.0.0.1:1080")
    # bot = Bot(token=settings.BOT_TOKEN, session=session)
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(public_router)
    dp.include_router(private_router)

    app.state.bot = bot
    app.state.dp = dp

    async with scheduler_manager(bot):
        await bot.set_webhook(settings.WEBHOOK_URL)
        yield
        await bot.delete_webhook()
        await bot.session.close()


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/telegram")


@router.post(settings.WEBHOOK_PATH)
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


@router.get("/resolve-link-token/")
async def resolve_link_token(token: str):
    return await resolve_token(token)


@router.post("/confirm-relink")
async def confirm_relink_router(token: str):
    return await confirm_relink(token)


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
