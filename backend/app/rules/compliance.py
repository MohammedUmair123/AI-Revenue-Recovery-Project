import json
from typing import Optional

from app.models import RevenueEvent


def compliance_block_reason(event: RevenueEvent) -> Optional[str]:
    """
    Hard compliance vetoes. Any of these must block ALL further contact,
    regardless of how promising the recovery odds look.
    """
    customer = event.customer
    if customer is None:
        return "no customer record on file"

    if customer.do_not_contact:
        return "customer flagged do_not_contact"

    ctx = json.loads(event.raw_context or "{}")
    if ctx.get("dispute_filed"):
        return "active payment dispute — legal/compliance hold"

    if ctx.get("opted_out"):
        return "customer opted out of recovery communications"

    return None
