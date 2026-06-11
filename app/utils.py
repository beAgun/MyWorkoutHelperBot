from config import settings
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.db.models import *
from app.db.database import session_manager
from app.db.models_repo import *
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError


async def resolve_token(token: str):
    serializer = URLSafeTimedSerializer(secret_key=settings.TG_LINK_TOKEN)

    try:
        data = serializer.loads(token, max_age=600)
    except (BadSignature, SignatureExpired):
        return HTMLResponse(
            "<h1>Ссылка недействительна или устарела</h1>",
            status_code=400,
        )

    site_user_id = data["site_user_id"]
    chat_id = data["chat_id"]

    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session, chat_id=chat_id)

        if not user:
            return HTMLResponse(
                "<h1>Пользователь не найден</h1>",
                status_code=404,
            )

        try:
            user.site_user_id = site_user_id
            await session.commit()
        except IntegrityError:
            await session.rollback()

            relink_token = serializer.dumps(
                {
                    "site_user_id": site_user_id,
                    "chat_id": chat_id,
                    "force": True,
                }
            )

            return HTMLResponse(
                f"""
                <h1>
                    Аккаунт на сайте с указанной почтой 
                    уже привязан к другому Telegram аккаунту
                </h1>

                <form action="/confirm-relink" method="post">
                    <input
                        type="hidden"
                        name="token"
                        value="{relink_token}"
                    />

                    <button type="submit">
                        Перепривязать аккаунт
                    </button>
                </form>
                """,
                status_code=409,
            )

    return HTMLResponse("<h1>Аккаунт успешно привязан ✅</h1>")


async def confirm_relink(token: str):

    serializer = URLSafeTimedSerializer(secret_key=settings.TG_LINK_TOKEN)

    try:
        data = serializer.loads(token, max_age=600)
    except (BadSignature, SignatureExpired):
        return HTMLResponse(
            "<h1>Ссылка недействительна или устарела</h1>",
            status_code=400,
        )

    if not data.get("force"):
        return HTMLResponse(
            "<h1>Некорректный токен</h1>",
            status_code=400,
        )

    site_user_id = data["site_user_id"]
    chat_id = data["chat_id"]

    async with session_manager() as session:
        old_user = await UserRepo.get_user_by_site_id(
            session,
            site_user_id=site_user_id,
        )

        if old_user:
            old_user.site_user_id = None

        user = await UserRepo.get_user_by_chat_id(
            session,
            chat_id=chat_id,
        )

        if not user:
            return HTMLResponse(
                "<h1>Пользователь не найден</h1>",
                status_code=404,
            )

        user.site_user_id = site_user_id
        await session.commit()

    return HTMLResponse("<h1>Аккаунт успешно перепривязан ✅</h1>")
