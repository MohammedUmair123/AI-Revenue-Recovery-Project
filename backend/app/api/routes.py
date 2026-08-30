import json
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RevenueEvent, AuditLog, EventStatus, Customer
from app.agent.detector import detect_at_risk_events
from app.agent.diagnoser import diagnose_event
from app.agent.decision_engine import decide_intervention
from app.agent.executor import execute_intervention
from app.services.audit import log_audit
from app.seed_data import reset_and_seed

router = APIRouter()


@router.post("/seed")
def seed(n_customers: int = 40, n_events: int = 120, db: Session = Depends(get_db)):
    reset_and_seed(n_customers, n_events)
    return {"status": "seeded", "customers": n_customers, "events": n_events}


@router.post("/run-batch")
def run_batch(limit: int = 200, db: Session = Depends(get_db)):
    """
    Runs the full detect -> diagnose -> decide -> act pipeline over the current
    open batch of revenue events. This is the core demo endpoint.
    """
    events = detect_at_risk_events(db, limit=limit)
    log_audit(db, stage="detect", summary=f"Batch run started: {len(events)} at-risk events detected.")

    results = []
    total_recovered = 0.0
    for event in events:
        diagnosis = diagnose_event(event)
        event.root_cause = diagnosis["root_cause"]
        event.diagnosis_confidence = diagnosis["confidence"]
        event.diagnosis_reasoning = diagnosis["reasoning"]
        log_audit(
            db,
            event_id=event.id,
            stage="diagnose",
            summary=f"Diagnosed event {event.id} as '{diagnosis['root_cause']}' (conf {diagnosis['confidence']:.2f})",
            detail=json.dumps(diagnosis),
        )

        decision = decide_intervention(event, diagnosis)
        log_audit(
            db,
            event_id=event.id,
            stage="decide",
            summary=f"Decision for event {event.id}: {decision['intervention'].value}",
            detail=json.dumps({k: (v.value if hasattr(v, "value") else v) for k, v in decision.items()}),
        )

        outcome = execute_intervention(db, event, decision)
        total_recovered += outcome["recovered_amount"]

        results.append(
            {
                "event_id": event.id,
                "root_cause": diagnosis["root_cause"],
                "intervention": decision["intervention"].value,
                "outcome": outcome["outcome"],
                "recovered_amount": outcome["recovered_amount"],
            }
        )

    db.commit()
    return {
        "events_processed": len(events),
        "total_recovered": round(total_recovered, 2),
        "results": results,
    }


@router.get("/events")
def list_events(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(RevenueEvent)
    if status:
        q = q.filter(RevenueEvent.status == status)
    events = q.order_by(RevenueEvent.created_at.desc()).limit(500).all()
    return [
        {
            "id": e.id,
            "customer_name": e.customer.name if e.customer else None,
            "event_type": e.event_type.value,
            "amount": e.amount,
            "status": e.status.value,
            "root_cause": e.root_cause,
            "diagnosis_confidence": e.diagnosis_confidence,
            "contact_attempts": e.contact_attempts,
            "amount_recovered": e.amount_recovered,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]


@router.get("/audit")
def audit_trail(event_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(AuditLog)
    if event_id:
        q = q.filter(AuditLog.event_id == event_id)
    logs = q.order_by(AuditLog.timestamp.desc()).limit(500).all()
    return [
        {
            "id": l.id,
            "event_id": l.event_id,
            "stage": l.stage,
            "actor": l.actor,
            "summary": l.summary,
            "detail": l.detail,
            "timestamp": l.timestamp.isoformat(),
        }
        for l in logs
    ]


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total_at_risk = db.query(func.sum(RevenueEvent.amount)).scalar() or 0.0
    total_recovered = db.query(func.sum(RevenueEvent.amount_recovered)).scalar() or 0.0
    total_events = db.query(func.count(RevenueEvent.id)).scalar() or 0
    recovered_count = (
        db.query(func.count(RevenueEvent.id))
        .filter(RevenueEvent.status == EventStatus.RECOVERED)
        .scalar()
        or 0
    )
    stopped_count = (
        db.query(func.count(RevenueEvent.id))
        .filter(RevenueEvent.status == EventStatus.STOPPED)
        .scalar()
        or 0
    )
    escalated_count = (
        db.query(func.count(RevenueEvent.id))
        .filter(RevenueEvent.status == EventStatus.ESCALATED)
        .scalar()
        or 0
    )

    by_cause = (
        db.query(RevenueEvent.root_cause, func.count(RevenueEvent.id), func.sum(RevenueEvent.amount_recovered))
        .filter(RevenueEvent.root_cause.isnot(None))
        .group_by(RevenueEvent.root_cause)
        .all()
    )

    return {
        "total_at_risk": round(total_at_risk, 2),
        "total_recovered": round(total_recovered, 2),
        "recovery_rate": round((total_recovered / total_at_risk) * 100, 1) if total_at_risk else 0.0,
        "total_events": total_events,
        "recovered_count": recovered_count,
        "stopped_count": stopped_count,
        "escalated_count": escalated_count,
        "by_cause": [
            {"root_cause": rc, "count": cnt, "recovered": round(rec or 0.0, 2)}
            for rc, cnt, rec in by_cause
        ],
    }
