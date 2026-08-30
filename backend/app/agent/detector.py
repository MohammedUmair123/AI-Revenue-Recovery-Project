from sqlalchemy.orm import Session

from app.models import RevenueEvent, EventStatus


def detect_at_risk_events(db: Session, limit: int = 200) -> list[RevenueEvent]:
    """
    Pulls the batch of revenue events that are still open (or mid-flow)
    and therefore represent money the business hasn't collected yet.
    This is intentionally simple: in production this stage would subscribe
    to webhooks (payment gateway declines, cart events, invoicing system)
    rather than poll a table.
    """
    return (
        db.query(RevenueEvent)
        .filter(RevenueEvent.status.in_([EventStatus.OPEN, EventStatus.IN_PROGRESS]))
        .order_by(RevenueEvent.amount.desc())
        .limit(limit)
        .all()
    )
