# Demo Script (3–4 minutes)

1. **Open the dashboard.** Empty ledger — nothing has been processed yet.

2. **Click "Seed Batch Data."** Explain: this generates ~120 synthetic
   at-risk events (failed payments, abandoned checkouts, failed subscription
   renewals, overdue invoices) across 40 customers — standing in for a real
   webhook feed from a payment gateway / cart tracker / invoicing system.

3. **Click "Run Recovery Batch."** Narrate the pipeline live:
   - "Each event is diagnosed by an LLM for root cause — card expired,
     price hesitation, cash-flow issue, etc."
   - "Before any action, it's checked against compliance rules — do-not-contact,
     active disputes — and stopping rules — max attempts, quiet hours, pursuit
     window. Those can veto action entirely."
   - "If it clears both, the decision engine picks the right intervention from
     a root-cause playbook and executes it — email, SMS, retry, escalation,
     promise-to-pay."

4. **Point at the Recovery Ledger bar** — total at risk vs. actually recovered,
   with a real recovery-rate percentage.

5. **Point at "Recovery by Root Cause"** — shows which failure modes are most
   recoverable, which is the actionable insight a revenue team would want.

6. **Open the Audit Trail panel** — scroll through entries showing detect →
   diagnose → decide → act (and stop, for blocked events) with reasoning
   attached to each. This is the accountability layer: every dollar recovered
   (or not pursued) has a paper trail.

7. **Close on the stopping-rule example**: click into an event that got
   `stopped` or `opted_out` in the table, and show in the audit trail exactly
   why the agent refused to keep contacting that customer — this is the
   "bounded" part of "bounded recovery workflow."
