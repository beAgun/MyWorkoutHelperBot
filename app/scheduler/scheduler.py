from contextlib import asynccontextmanager
from datetime import datetime

# from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.infra.http_client import HttpClient
from app.scheduler.jobs import (
    check_kgbrun_registration_open,
    check_med_schedule,
    create_http_client,
    send_trainings_notifications,
)
from logger import logger

# jobstores = {'redis': RedisJobStore()}
job_defaults = {"coalesce": True, "max_instances": 1}
executors = {"async_executor": AsyncIOExecutor()}
scheduler = AsyncIOScheduler(executors=executors, job_defaults=job_defaults)

client = None


@asynccontextmanager
async def scheduler_manager(app):
    try:
        scheduler.add_job(
            send_trainings_notifications,
            trigger=IntervalTrigger(seconds=30),
            id="send_trainings_notifications_job",
            replace_existing=True,
            max_instances=1,
            args=[app.state.sender],
        )

        client = await create_http_client()
        scheduler.add_job(
            check_kgbrun_registration_open,
            id="check_kgbrun_registration_open_job",
            replace_existing=True,
            trigger=IntervalTrigger(seconds=5 * 60),
            max_instances=1,
            next_run_time=datetime.now(),
            args=[client.session, app.state.sender],
        )

        med_client = HttpClient(base_url="https://gorzdrav.spb.ru/")
        med_session = await med_client.get_session()
        scheduler.add_job(
            check_med_schedule,
            id="check_med_schedule_job",
            replace_existing=True,
            trigger=IntervalTrigger(seconds=30 * 60),
            max_instances=1,
            next_run_time=datetime.now(),
            args=[med_session, app.state.sender],
        )

        if not scheduler.running:
            scheduler.start()
        yield scheduler
    finally:
        if scheduler.running:
            scheduler.shutdown()
            if client:
                await client.close()
