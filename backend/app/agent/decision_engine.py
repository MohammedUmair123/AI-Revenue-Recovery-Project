from app.models import RevenueEvent, EventType, InterventionType
from app.rules.stopping_rules import should_stop_pursuit
from app.rules.compliance import compliance_block_reason


# Root-cause -> preferred intervention ladder.
# The agent walks this ladder based on contact_attempts so far (escalating gently).
CAUSE_PLAYBOOK: dict[str, list[InterventionType]] = {
    "card_expired": [InterventionType.SEND_REMINDER_EMAIL, InterventionType.SEND_SMS_NUDGE],
    "insufficient_funds": [InterventionType.AUTO_RETRY_PAYMENT, InterventionType.SEND_REMINDER_EMAIL],
    "gateway_timeout": [InterventionType.AUTO_RETRY_PAYMENT],
    "invalid_cvv": [InterventionType.SEND_REMINDER_EMAIL],
    "bank_declined_risk_flag": [InterventionType.ESCALATE_TO_HUMAN],
    "price_hesitation": [InterventionType.OFFER_DISCOUNT, InterventionType.SEND_REMINDER_EMAIL],
    "distracted_checkout": [InterventionType.SEND_REMINDER_EMAIL, InterventionType.SEND_SMS_NUDGE],
    "unexpected_fees": [InterventionType.SEND_REMINDER_EMAIL, InterventionType.OFFER_DISCOUNT],
    "high_shipping_cost_shown": [InterventionType.OFFER_DISCOUNT],
    "chronic_late_payer": [InterventionType.SEND_REMINDER_EMAIL, InterventionType.ESCALATE_TO_HUMAN],
    "cash_flow_issue_b2b": [InterventionType.OFFER_GRACE_PERIOD, InterventionType.MARK_PROMISE_TO_PAY],
    "invoice_overlooked": [InterventionType.SEND_REMINDER_EMAIL],
    "dispute_risk": [InterventionType.ESCALATE_TO_HUMAN],
    "genuine_non_intent": [InterventionType.NO_ACTION],
}

DEFAULT_LADDER = [InterventionType.SEND_REMINDER_EMAIL, InterventionType.ESCALATE_TO_HUMAN]


def decide_intervention(event: RevenueEvent, diagnosis: dict) -> dict:
    """
    Returns a decision dict: {
        "intervention": InterventionType,
        "reasoning": str,
        "blocked": bool,
        "block_reason": str | None,
    }
    Compliance and stopping rules are checked BEFORE any intervention is chosen —
    they can veto action entirely regardless of what the playbook suggests.
    """
    # 1. Compliance gate (do-not-contact, quiet hours, opt-out) — hard veto.
    block_reason = compliance_block_reason(event)
    if block_reason:
        return {
            "intervention": InterventionType.NO_ACTION,
            "reasoning": f"Compliance block: {block_reason}",
            "blocked": True,
            "block_reason": block_reason,
        }

    # 2. Stopping rules (max attempts, max pursuit days, already recovered) — hard veto.
    stop_reason = should_stop_pursuit(event)
    if stop_reason:
        return {
            "intervention": InterventionType.NO_ACTION,
            "reasoning": f"Stopping rule triggered: {stop_reason}",
            "blocked": True,
            "block_reason": stop_reason,
        }

    # 3. Pick from the playbook ladder for this root cause, escalating with attempts.
    ladder = CAUSE_PLAYBOOK.get(diagnosis["root_cause"], DEFAULT_LADDER)
    rung = min(event.contact_attempts, len(ladder) - 1)
    intervention = ladder[rung]

    # B2B invoices always prefer promise-to-pay tracking once a human channel opens.
    if event.event_type == EventType.INVOICE_OVERDUE and event.contact_attempts >= 2:
        intervention = InterventionType.ESCALATE_TO_HUMAN

    reasoning = (
        f"Root cause '{diagnosis['root_cause']}' (confidence {diagnosis['confidence']:.2f}) "
        f"-> playbook rung {rung + 1}/{len(ladder)}: {intervention.value}."
    )
    return {
        "intervention": intervention,
        "reasoning": reasoning,
        "blocked": False,
        "block_reason": None,
    }
