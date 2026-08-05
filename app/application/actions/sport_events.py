from app.db.database import session_manager
from app.db.models_repo import CompetitionMonitorStateRepo
from app.db.models import CompetitionMonitorState


async def get_sport_event_log() -> list[CompetitionMonitorState]:
    async with session_manager() as session:
        events = await CompetitionMonitorStateRepo.get_all(session)
    return events
