from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from contextlib import asynccontextmanager
from app.scheduler.jobs import send_trainings_notifications
from apscheduler.triggers.interval import IntervalTrigger
from logger import logger


# jobstores = {'redis': RedisJobStore()}
job_defaults = {"coalesce": True, "max_instances": 1}
executors = {"async_executor": AsyncIOExecutor()}
scheduler = AsyncIOScheduler(executors=executors, job_defaults=job_defaults)


@asynccontextmanager
async def scheduler_manager(bot):
    try:
        scheduler.add_job(
            send_trainings_notifications,
            trigger=IntervalTrigger(seconds=30),
            id="send_trainings_notifications_job",
            replace_existing=True,
            args=[bot],
        )
        scheduler.start()
        yield scheduler
    finally:
        if scheduler.running:
            scheduler.shutdown()
