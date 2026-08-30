import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Boolean,
    Text,
)
from sqlalchemy.orm import relationship

from app.db import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class EventType(str, enum.Enum):
    PAYMENT_FAILED = "payment_failed"
    CHECKOUT_ABANDONED = "checkout_abandoned"
    SUBSCRIPTION_FAILED = "subscription_failed"
    INVOICE_OVERDUE = "invoice_overdue"


class EventStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RECOVERED = "recovered"
    STOPPED = "stopped"          # stopping rule triggered, gave up
    ESCALATED = "escalated"       # handed to a human
    OPTED_OUT = "opted_out"       # compliance: customer opted out


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    segment = Column(String, default="standard")  # e.g. "b2b", "consumer", "vip"
    do_not_contact = Column(Boolean, default=False)
    lifetime_value = Column(Float, default=0.0)
    chronic_late_payer = Column(Boolean, default=False)

    events = relationship("RevenueEvent", back_populates="customer")


class RevenueEvent(Base):
    __tablename__ = "revenue_events"

    id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.id"))
    event_type = Column(Enum(EventType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(EventStatus), default=EventStatus.OPEN)

    # Raw signal data (differs per event type) kept as free text/JSON string
    raw_context = Column(Text, nullable=True)

    root_cause = Column(String, nullable=True)         # set by diagnoser
    diagnosis_confidence = Column(Float, nullable=True)
    diagnosis_reasoning = Column(Text, nullable=True)

    contact_attempts = Column(Integer, default=0)
    amount_recovered = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="events")
    actions = relationship("InterventionAction", back_populates="event")


class InterventionType(str, enum.Enum):
    AUTO_RETRY_PAYMENT = "auto_retry_payment"
    SEND_REMINDER_EMAIL = "send_reminder_email"
    SEND_SMS_NUDGE = "send_sms_nudge"
    OFFER_GRACE_PERIOD = "offer_grace_period"
    OFFER_DISCOUNT = "offer_discount"
    MARK_PROMISE_TO_PAY = "mark_promise_to_pay"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    NO_ACTION = "no_action"


class InterventionAction(Base):
    __tablename__ = "intervention_actions"

    id = Column(String, primary_key=True, default=gen_id)
    event_id = Column(String, ForeignKey("revenue_events.id"))
    intervention_type = Column(Enum(InterventionType), nullable=False)
    reasoning = Column(Text, nullable=True)
    outcome = Column(String, nullable=True)  # e.g. "sent", "skipped", "recovered"
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("RevenueEvent", back_populates="actions")


class AuditLog(Base):
    """Append-only audit trail. Never updated or deleted after write."""

    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=gen_id)
    event_id = Column(String, ForeignKey("revenue_events.id"), nullable=True)
    stage = Column(String, nullable=False)  # detect | diagnose | decide | act | stop
    actor = Column(String, default="agent")  # agent | system | human
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=True)     # JSON string with full reasoning/payload
    timestamp = Column(DateTime, default=datetime.utcnow)
