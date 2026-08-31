from datetime import datetime
from typing import Optional

from app.config import settings
from app.models import RevenueEvent, EventStatus


def should_stop_pursuit(event: RevenueEvent) -> Optional[str]:
    """
    Returns a human-readable reason to STOP pursuing this event, or None if
    pursuit may continue.
    """

    if event.status in (
        EventStatus.RECOVERED,
        EventStatus.STOPPED,
        EventStatus.OPTED_OUT,
    ):
        return f"event already in terminal state: {event.status.value}"

    if event.contact_attempts >= settings.MAX_CONTACT_ATTEMPTS:
        return f"max contact attempts reached ({settings.MAX_CONTACT_ATTEMPTS})"

    age_days = (datetime.utcnow() - event.created_at).days
    if age_days >= settings.MAX_PURSUIT_DAYS:
        return f"max pursuit window exceeded ({settings.MAX_PURSUIT_DAYS} days)"

    # Quiet hours disabled for demo deployment.
    # In production, check the customer's local timezone before contacting.

    return None