import logging

import httpx

from app.config import settings
from app.models import RevenueEvent, InterventionType

logger = logging.getLogger("notifier")

TEMPLATES = {
    InterventionType.SEND_REMINDER_EMAIL: (
        "Action Required: Payment Could Not Be Processed",
        """
        Hi {name},

    We attempted to process your recent payment of ${amount:.2f}, but unfortunately it was unsuccessful.

    To avoid any interruption to your account or services, please update your payment method or retry your payment at your earliest convenience.

    If you've already resolved this issue, you can safely ignore this message.

    Thank you,
    The Support Team""".strip(),
    ),

    InterventionType.OFFER_DISCOUNT: (
        "Complete Your Purchase & Save",
        """
    Hi {name},

    We noticed that your order worth ${amount:.2f} is still waiting in your cart.

    Complete your purchase within the next 24 hours and we'll automatically apply an exclusive discount at checkout.

    We'd love to have you back!

    Best regards,
    The Sales Team""".strip(),
    ),

    InterventionType.OFFER_GRACE_PERIOD: (
        "Your Payment Deadline Has Been Extended",
        """
    Hi {name},

    We understand that payment timing doesn't always go as planned.

    To make things easier, we've extended the payment deadline for your outstanding balance of ${amount:.2f}. No additional action is required until the new due date.

    If you have any questions, we're always here to help.

    Best regards,
    The Billing Team""".strip(),
    ),
}


def send_reminder_email(event: RevenueEvent, intervention: InterventionType) -> bool:
    print(">>> send_reminder_email CALLED <<<", flush=True)
    customer = event.customer
    subject, body_template = TEMPLATES.get(
        intervention, TEMPLATES[InterventionType.SEND_REMINDER_EMAIL]
    )
    body = body_template.format(name=customer.name, amount=event.amount)
    
    print("SEND_REAL_EMAILS =", settings.SEND_REAL_EMAILS, flush=True)
    print("API KEY =", settings.RESEND_API_KEY, flush=True)
    print("API KEY LENGTH =", len(settings.RESEND_API_KEY), flush=True)

    if not settings.SEND_REAL_EMAILS or not settings.RESEND_API_KEY:
        logger.info("[SIMULATED EMAIL] to=%s subject=%s body=%s", customer.email, subject, body)
        return True

    # TESTING ONLY: Resend won't deliver to arbitrary/fake addresses until a
    # domain is verified, so redirect to a real inbox you control if set.
    # The original (fake) customer email is kept in the subject/body context
    # and logged, so nothing about the recovery logic itself changes.
    recipient = settings.TEST_RECIPIENT_EMAIL or customer.email
    if settings.TEST_RECIPIENT_EMAIL:
        subject = f"[TEST → {customer.name} <{customer.email}>] {subject}"
        logger.info(
            "Redirecting real send from fake customer email %s to test recipient %s",
            customer.email,
            recipient,
        )
    print("Recipient:", recipient, flush=True)
    print("From:", settings.RESEND_FROM_EMAIL, flush=True)
    print("API Key Present:", bool(settings.RESEND_API_KEY), flush=True)
    print("SEND_REAL_EMAILS:", settings.SEND_REAL_EMAILS, flush=True)
    print("Sending request to Resend...", flush=True)

    try:
        print("Before httpx.post()", flush=True)
        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={
                "from": settings.RESEND_FROM_EMAIL,
                "to": [recipient],
                "subject": subject,
                "text": body,
            },
            timeout=10.0,
        )
        print("After httpx.post()", flush=True)
        print(resp.status_code, flush=True)
        print(resp.text, flush=True)
        resp.raise_for_status()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Email send failed, falling back to log-only: %s", exc)
        return False


def send_sms_nudge(event: RevenueEvent) -> bool:
    """
    SMS is simulated/logged only in this free scaffold (real SMS requires a paid
    Twilio/MSG91 number). Swap this out for a real provider in production.
    """
    customer = event.customer
    message = f"Hi {customer.name}, quick reminder about your ${event.amount:.2f} payment. Tap to fix: [link]"
    logger.info("[SIMULATED SMS] to=%s message=%s", customer.phone, message)
    return True
