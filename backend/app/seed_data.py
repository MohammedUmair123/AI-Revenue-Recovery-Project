import json
import random
from datetime import datetime, timedelta

from faker import Faker

from app.db import SessionLocal
from app.models import Customer, RevenueEvent, EventType, EventStatus

fake = Faker()

PAYMENT_FAIL_REASONS = [
    "card_expired",
    "insufficient_funds",
    "gateway_timeout",
    "bank_declined_risk_flag",
    "invalid_cvv",
]

CHECKOUT_DROP_REASONS = [
    "high_shipping_cost_shown",
    "price_hesitation",
    "distracted_left_tab",
    "payment_form_error",
    "unexpected_fees",
]


def _random_past_datetime(max_days_ago=14):
    return datetime.utcnow() - timedelta(
        days=random.randint(0, max_days_ago),
        hours=random.randint(0, 23),
    )


def generate_batch(db, n_customers=40, n_events=120):
    customers = []
    for _ in range(n_customers):
        segment = random.choices(
            ["consumer", "b2b", "vip"], weights=[0.6, 0.3, 0.1]
        )[0]
        c = Customer(
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            segment=segment,
            do_not_contact=random.random() < 0.05,
            lifetime_value=round(random.uniform(50, 20000), 2),
            chronic_late_payer=random.random() < 0.15,
        )
        db.add(c)
        customers.append(c)
    db.flush()  # get IDs

    events = []
    for _ in range(n_events):
        customer = random.choice(customers)
        event_type = random.choices(
            list(EventType),
            weights=[0.35, 0.30, 0.15, 0.20],  # payment, checkout, sub, invoice
        )[0]

        if event_type == EventType.PAYMENT_FAILED:
            amount = round(random.uniform(15, 500), 2)
            context = {"decline_reason_code": random.choice(PAYMENT_FAIL_REASONS)}
        elif event_type == EventType.CHECKOUT_ABANDONED:
            amount = round(random.uniform(20, 800), 2)
            context = {
                "cart_reason_signal": random.choice(CHECKOUT_DROP_REASONS),
                "cart_age_minutes": random.randint(5, 300),
            }
        elif event_type == EventType.SUBSCRIPTION_FAILED:
            amount = round(random.choice([9.99, 19.99, 29.99, 49.99, 99.0]), 2)
            context = {
                "failed_renewal_count": random.randint(1, 3),
                "decline_reason_code": random.choice(PAYMENT_FAIL_REASONS),
            }
        else:  # INVOICE_OVERDUE
            amount = round(random.uniform(500, 15000), 2)
            context = {
                "days_overdue": random.randint(1, 60),
                "invoice_terms": random.choice(["net_15", "net_30", "net_45"]),
            }

        e = RevenueEvent(
            customer_id=customer.id,
            event_type=event_type,
            amount=amount,
            currency="USD",
            status=EventStatus.OPEN,
            raw_context=json.dumps(context),
            created_at=_random_past_datetime(),
        )
        db.add(e)
        events.append(e)

    db.commit()
    return customers, events


def reset_and_seed(n_customers=40, n_events=120):
    db = SessionLocal()
    try:
        db.query(RevenueEvent).delete()
        db.query(Customer).delete()
        db.commit()
        generate_batch(db, n_customers, n_events)
    finally:
        db.close()
