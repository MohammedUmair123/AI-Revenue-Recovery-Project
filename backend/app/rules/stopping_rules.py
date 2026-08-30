from datetime import datetime
from typing import Optional

from app.config import settings
from app.models import RevenueEvent, EventStatus


def should_stop_pursuit(event: RevenueEvent) -> Optional[str]:
    """
    Returns a human-readable reason to STOP pursuing this event, or None if
    pursuit may continue. These are hard limits — the decision engine cannot
    override them.
    """
    if event.status in (EventStatus.RECOVERED, EventStatus.STOPPED, EventStatus.OPTED_OUT):
        return f"event already in terminal state: {event.status.value}"

    if event.contact_attempts >= settings.MAX_CONTACT_ATTEMPTS:
        return f"max contact attempts reached ({settings.MAX_CONTACT_ATTEMPTS})"

    age_days = (datetime.utcnow() - event.created_at).days
    if age_days >= settings.MAX_PURSUIT_DAYS:
        return f"max pursuit window exceeded ({settings.MAX_PURSUIT_DAYS} days)"

    now_hour = datetime.utcnow().hour
    in_quiet_hours = (
        now_hour >= settings.QUIET_HOURS_START or now_hour < settings.QUIET_HOURS_END
    )
    if in_quiet_hours:
        return "within quiet hours — contact deferred to next allowed window"

    return None
