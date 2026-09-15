from app.infra.redis_infra.redis_client import redis_client


async def get_med_schedule_status() -> str:
    med_status = await redis_client.get("med_status")
    return med_status | ""
