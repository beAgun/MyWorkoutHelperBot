import asyncio
from app.infra.redis_infra.consumers.workouts_consumer import start_consumer

if __name__ == "__main__":
    asyncio.run(start_consumer())
