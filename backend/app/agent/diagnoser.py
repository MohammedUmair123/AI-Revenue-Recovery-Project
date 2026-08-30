import json

from app.llm_client import call_llm_json
from app.models import RevenueEvent, EventType

SYSTEM_PROMPT = """You are a revenue recovery diagnostic engine for a business.
Given a single revenue-at-risk event, determine the most likely ROOT CAUSE and
how confident you are. Root causes should be short snake_case tags such as:
card_expired, insufficient_funds, gateway_timeout, price_hesitation,
distracted_checkout, chronic_late_payer, dispute_risk, unexpected_fees,
technical_error, cash_flow_issue_b2b, genuine_non_intent.

Return JSON with exactly these keys:
{
  "root_cause": "<snake_case tag>",
  "confidence": <float 0-1>,
  "reasoning": "<1-2 sentence explanation>"
}
"""


def _fallback_diagnosis(event: RevenueEvent) -> dict:
    """Deterministic rule-based fallback so the pipeline works with no API key."""
    ctx = json.loads(event.raw_context or "{}")
    if event.event_type == EventType.PAYMENT_FAILED:
        cause = ctx.get("decline_reason_code", "unknown_decline")
    elif event.event_type == EventType.CHECKOUT_ABANDONED:
        cause = ctx.get("cart_reason_signal", "unknown_abandonment")
    elif event.event_type == EventType.SUBSCRIPTION_FAILED:
        cause = ctx.get("decline_reason_code", "renewal_failure")
    else:
        cause = "cash_flow_issue_b2b" if ctx.get("days_overdue", 0) > 20 else "invoice_overlooked"
    return {
        "root_cause": cause,
        "confidence": 0.6,
        "reasoning": "Rule-based fallback classification from raw event context.",
    }


def diagnose_event(event: RevenueEvent) -> dict:
    ctx = json.loads(event.raw_context or "{}")
    user_prompt = f"""
Event type: {event.event_type.value}
Amount: {event.amount} {event.currency}
Customer segment: {event.customer.segment if event.customer else "unknown"}
Chronic late payer: {event.customer.chronic_late_payer if event.customer else False}
Prior contact attempts: {event.contact_attempts}
Raw context: {json.dumps(ctx)}
"""
    result = call_llm_json(SYSTEM_PROMPT, user_prompt)
    if result.get("_fallback"):
        fb = _fallback_diagnosis(event)
        fb["reasoning"] = result.get("reasoning", "") + " " + fb["reasoning"]
        return fb

    return {
        "root_cause": result.get("root_cause", "unknown"),
        "confidence": float(result.get("confidence", 0.5)),
        "reasoning": result.get("reasoning", ""),
    }
