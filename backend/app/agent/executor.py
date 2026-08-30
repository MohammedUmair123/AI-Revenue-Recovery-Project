import json
import random
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    RevenueEvent,
    EventStatus,
    InterventionAction,
    InterventionType,
    AuditLog,
)
from app.services.notifier import send_reminder_email, send_sms_nudge
from app.services.audit import log_audit

# Simulated recovery-success probabilities per intervention type.
# In a real system this would come from actually retrying the payment gateway,
# or from webhook confirmation that an invoice was paid / cart was completed.
SUCCESS_PROBABILITY = {
    InterventionType.AUTO_RETRY_PAYMENT: 0.45,
    InterventionType.SEND_REMINDER_EMAIL: 0.28,
    InterventionType.SEND_SMS_NUDGE: 0.22,
    InterventionType.OFFER_GRACE_PERIOD: 0.35,
    InterventionType.OFFER_DISCOUNT: 0.40,
    InterventionType.MARK_PROMISE_TO_PAY: 0.55,  # tracked separately, resolved later
    InterventionType.ESCALATE_TO_HUMAN: 0.50,
    InterventionType.NO_ACTION: 0.0,
}


def execute_intervention(db: Session, event: RevenueEvent, decision: dict) -> dict:
    intervention: InterventionType = decision["intervention"]

    if decision["blocked"]:
        event.status = (
            EventStatus.OPTED_OUT
            if "opt" in (decision["block_reason"] or "").lower()
            or "do_not_contact" in (decision["block_reason"] or "")
            else EventStatus.STOPPED
        )
        action = InterventionAction(
            event_id=event.id,
            intervention_type=InterventionType.NO_ACTION,
            reasoning=decision["reasoning"],
            outcome="blocked",
        )
        db.add(action)
        log_audit(
            db,
            event_id=event.id,
            stage="stop",
            summary=f"Pursuit halted for event {event.id}: {decision['block_reason']}",
            detail=json.dumps(decision),
        )
        return {"outcome": "blocked", "recovered_amount": 0.0}

    if intervention == InterventionType.ESCALATE_TO_HUMAN:
        event.status = EventStatus.ESCALATED
        outcome = "escalated"
    elif intervention == InterventionType.MARK_PROMISE_TO_PAY:
        event.status = EventStatus.IN_PROGRESS
        outcome = "promise_to_pay_logged"
    else:
        event.status = EventStatus.IN_PROGRESS
        outcome = "sent"

    # --- Actually perform the side-effecting action (bounded, logged) ---
    if intervention in (InterventionType.SEND_REMINDER_EMAIL, InterventionType.OFFER_DISCOUNT,
                        InterventionType.OFFER_GRACE_PERIOD):
        send_reminder_email(event, intervention)
    elif intervention == InterventionType.SEND_SMS_NUDGE:
        send_sms_nudge(event)
    # AUTO_RETRY_PAYMENT / ESCALATE_TO_HUMAN / MARK_PROMISE_TO_PAY have no external
    # notification side effect in this scaffold — wire to a real payment gateway
    # or CRM ticket API here in production.

    event.contact_attempts += 1

    # --- Simulate whether this action recovered the money ---
    recovered_amount = 0.0
    p_success = SUCCESS_PROBABILITY.get(intervention, 0.0)
    if random.random() < p_success and intervention != InterventionType.MARK_PROMISE_TO_PAY:
        recovered_amount = event.amount
        event.amount_recovered = recovered_amount
        event.status = EventStatus.RECOVERED
        event.resolved_at = datetime.utcnow()
        outcome = "recovered"

    action = InterventionAction(
        event_id=event.id,
        intervention_type=intervention,
        reasoning=decision["reasoning"],
        outcome=outcome,
    )
    db.add(action)

    log_audit(
        db,
        event_id=event.id,
        stage="act",
        summary=f"Executed {intervention.value} on event {event.id}: outcome={outcome}",
        detail=json.dumps(
            {
                "intervention": intervention.value,
                "reasoning": decision["reasoning"],
                "recovered_amount": recovered_amount,
                "contact_attempts": event.contact_attempts,
            }
        ),
    )

    return {"outcome": outcome, "recovered_amount": recovered_amount}
