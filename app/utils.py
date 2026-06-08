from config import settings
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.db.models import *
from app.db.database import session_manager
from app.db.models_repo import *
from fastapi.responses import HTMLResponse


async def resolve_token(token: str):
    serializer = URLSafeTimedSerializer(secret_key=settings.TG_LINK_TOKEN)

    try:
        data = serializer.loads(token, max_age=600)
    except (BadSignature, SignatureExpired):
        return HTMLResponse("<h1>Ссылка недействительна или устарела</h1>")

    site_user_id = data["site_user_id"]
    chat_id = data["chat_id"]

    async with session_manager() as session:
        user = await UserRepo.get_user_by_chat_id(session, chat_id=chat_id)

        if not user:
            return HTMLResponse("<h1>Пользователь не найден</h1>")

        user.site_user_id = site_user_id
        await session.commit()

    return HTMLResponse("<h1>Аккаунт успешно привязан ✅</h1>")
