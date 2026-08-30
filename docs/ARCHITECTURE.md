# Architecture

## Pipeline

```
DETECT → DIAGNOSE → DECIDE → ACT → TRACK → AUDIT
```

1. **Detect** (`app/agent/detector.py`) — pulls open/in-progress `RevenueEvent`
   rows: failed payments, abandoned checkouts, failed subscription renewals,
   overdue invoices. In production this would be event-driven (webhooks from
   a payment gateway, cart tracker, and invoicing system) rather than polling.

2. **Diagnose** (`app/agent/diagnoser.py`) — calls Groq (Llama 3.3) to classify
   a short, structured root cause with a confidence score and reasoning. Falls
   back to a deterministic rule-based classifier if no API key is configured,
   so the whole pipeline still runs without any signup.

3. **Decide** (`app/agent/decision_engine.py`) — **compliance and stopping
   rules run first and can veto action outright.** Only if the event clears
   both gates does the engine pick an intervention from a root-cause playbook,
   escalating gently as `contact_attempts` increases (e.g. email → SMS →
   escalate to a human).

4. **Act** (`app/agent/executor.py`) — executes the bounded action (send
   email/SMS, retry payment, log a promise-to-pay, escalate). Every action
   increments `contact_attempts`, so stopping rules keep tightening the leash
   on later runs.

5. **Track** — `amount_recovered` and `status` update on the event row.
   Recovery is simulated with a probability per intervention type in this
   scaffold — swap in a real payment-gateway retry call or webhook confirmation
   for production.

6. **Audit** (`app/services/audit.py`, `AuditLog` model) — every stage writes
   an append-only row: what was decided, why, and the outcome. Nothing is ever
   updated or deleted. This is what makes the batch run reviewable/defensible,
   not just a black box.

## Compliance & stopping rules (the "bar")

- `app/rules/compliance.py` — hard vetoes: `do_not_contact` flag, active
  dispute, customer opt-out. These override everything else.
- `app/rules/stopping_rules.py` — hard limits: max contact attempts, max
  pursuit window (days), quiet hours. Configurable in `app/config.py`.

## Data model

- `Customer` — identity, segment, do-not-contact flag, chronic-late-payer flag
- `RevenueEvent` — one row per at-risk event (payment/checkout/subscription/invoice)
- `InterventionAction` — one row per action taken on an event
- `AuditLog` — append-only trail across all stages

## Why a single unified pipeline

The brief's "example directions" (payment degradation, checkout drop-off,
failed-subscription recovery, B2B receivables chasing, mandate retry
sequencing, promise-to-pay tracking) are all instances of the same shape:
*detect a risk signal → diagnose why → pick a bounded intervention → track
recovery → audit the decision*. Building one pipeline over a generic
`RevenueEvent` model covers all of them, instead of five disconnected demos.
