from app.infra.site_client import SiteClient
from email_validator import validate_email, EmailNotValidError


def validate_user_email(email: str) -> str | None:
    try:
        return validate_email(email).email
    except EmailNotValidError:
        return None


async def get_email_link(email: str, chat_id: int) -> str:
    async with SiteClient() as site_session:
        response = await site_session.send_email_link(email, chat_id)

    if response.status == 200:
        return "Проверьте почту и перейдите по ссылке для завершения привязки аккаунтов"

    elif response.status == 404:
        return "Пользователь с указанной почтой не найден. Проверьте корректность и попробуйте снова"

    else:
        return "Произошла ошибка"


async def request_email_link(email: str, chat_id: int) -> str:
    validated_email = validate_user_email(email)
    if validated_email is None:
        raise ValueError(f"Формат адреса почты неверный. Введите заново")

    msg = await get_email_link(email=validated_email, chat_id=chat_id)
    return msg
