from typing import Optional

from sqlalchemy.orm import Session

from app.models import AuditLog


def log_audit(
    db: Session,
    stage: str,
    summary: str,
    event_id: Optional[str] = None,
    actor: str = "agent",
    detail: Optional[str] = None,
) -> None:
    entry = AuditLog(
        event_id=event_id,
        stage=stage,
        actor=actor,
        summary=summary,
        detail=detail,
    )
    db.add(entry)
