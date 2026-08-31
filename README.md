# AI Revenue Recovery Agent

## 🚀 Live Demo

**Try the project here:**  
👉 **https://airevenue-recovery-project1.vercel.app/**

No setup required. Simply:

1. Click **Seed Batch Data**
2. Click **Run Recovery Batch**
3. Watch the AI agent detect revenue at risk, diagnose the cause, decide the best intervention, and execute recovery actions.

---

## Overview

Businesses lose revenue every day because of:

- Failed payments
- Abandoned carts
- Failed subscription renewals
- Overdue invoices

This project demonstrates an **AI-powered Revenue Recovery Agent** that automatically:

- Detects revenue at risk
- Diagnoses why the payment failed using an LLM
- Chooses the best recovery strategy
- Enforces compliance and stopping rules
- Sends recovery emails
- Records every action in an audit trail

The dashboard visualizes recovery metrics, root causes, and the complete decision history.

---

## Features

### 🤖 AI Diagnosis
Uses **Groq (Llama 3.3 70B)** to determine the most likely reason behind each revenue loss.

Examples:

- Card expired
- Insufficient funds
- Customer abandoned checkout
- Invoice overlooked
- Price hesitation

---

### 🧠 Intelligent Decision Engine

Based on the diagnosis, the agent decides whether to:

- Retry payment
- Send reminder email
- Send SMS reminder
- Offer discount
- Offer grace period
- Escalate to a human
- Stop recovery

---

### ✅ Compliance & Safety

Before taking any action, the system checks:

- Do Not Contact customers
- Customer opt-outs
- Active payment disputes
- Maximum contact attempts
- Maximum recovery window
- Quiet hours (disabled only in demo mode)

---

### 📧 Real Email Integration

Supports real email delivery using **Resend**.

For demo purposes, recovery emails are delivered directly to the configured test inbox.

---

### 📊 Dashboard

The React dashboard displays:

- Total revenue at risk
- Total recovered amount
- Recovery rate
- Root cause analysis
- Recovery audit trail
- Event history

---

## Architecture

```
Detect At-Risk Events
          │
          ▼
Diagnose Root Cause (LLM)
          │
          ▼
Decision Engine
          │
          ▼
Compliance Checks
          │
          ▼
Stopping Rules
          │
          ▼
Execute Recovery
          │
     ┌────┴────┐
     │         │
 Email      Payment Retry
     │
     ▼
Update Database
     │
     ▼
Dashboard & Audit Logs
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | FastAPI |
| Database | SQLite |
| AI Model | Groq (Llama 3.3 70B) |
| Email | Resend |
| Deployment | Vercel + Render |

---

## Run Locally

### Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

---

### Frontend

```bash
cd frontend

npm install

cp .env.example .env

npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## Environment Variables

### Backend

```
GROQ_API_KEY=your_key
RESEND_API_KEY=your_key
SEND_REAL_EMAILS=true
TEST_RECIPIENT_EMAIL=your_email@example.com
```

### Frontend

```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Demo Workflow

1. Seed synthetic revenue events
2. Detect at-risk revenue
3. Diagnose root cause using AI
4. Decide the best recovery strategy
5. Execute recovery actions
6. Send recovery emails
7. Update dashboard metrics
8. Record every decision in the audit log

---

## Project Structure

```
ai-revenue-recovery/
│
├── backend/        FastAPI backend
├── frontend/       React dashboard
├── docs/           Architecture & demo guide
└── README.md
```

---

## Current Implementation

| Feature | Status |
|---------|--------|
| AI Root Cause Diagnosis | ✅ |
| Decision Engine | ✅ |
| Compliance Rules | ✅ |
| Stopping Rules | ✅ |
| Recovery Emails | ✅ |
| Dashboard | ✅ |
| Audit Trail | ✅ |
| Synthetic Data Generator | ✅ |
| Deployment | ✅ |

---

## Future Improvements

- Twilio SMS integration
- Stripe payment retries
- PostgreSQL support
- Multi-tenant architecture
- Live webhook ingestion
- Analytics dashboard
