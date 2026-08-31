# AI Revenue Recovery Agent

An AI-powered system that automatically detects revenue at risk, identifies the root cause using an LLM, decides the best recovery strategy, and executes recovery actions while enforcing compliance rules and maintaining a complete audit trail.

![image alt](Robot_Image.png)

---

# 🚀 Live Demo

### Frontend
**https://airevenue-recovery-project1.vercel.app/**

### How to Test

1. Open the live application.
2. Click **Seed Batch Data** to generate synthetic customer events.
3. Click **Run Recovery Batch**.
4. Watch the AI:
   - Detect at-risk revenue
   - Diagnose the root cause
   - Decide the best intervention
   - Send recovery emails
   - Update the dashboard
   - Record every action in the audit trail

No local setup is required to try the project.

---

# 📖 Overview

Businesses lose revenue every day due to:

- Failed payments
- Abandoned shopping carts
- Failed subscription renewals
- Overdue invoices

This project automates the recovery process using AI.

Instead of manually contacting customers, the system:

- Detects revenue at risk
- Uses an LLM to diagnose why the payment failed
- Chooses the most suitable recovery action
- Applies compliance and stopping rules
- Sends recovery emails
- Updates recovery metrics
- Stores every decision in an audit log

---

# ✨ Features

## 🤖 AI Root Cause Diagnosis

The application uses **OpenAI GPT-OSS-120B** through the **Groq API** to identify why a payment or transaction failed.

Example root causes include:

- Card expired
- Insufficient funds
- Invalid CVV
- Payment gateway timeout
- Price hesitation
- Customer abandoned checkout
- Invoice overlooked
- High shipping cost
- Cash flow issues
- Bank declined transaction

---

## 🧠 AI Decision Engine

Based on the diagnosis, the agent automatically decides the most appropriate recovery action.

Possible actions include:

- Retry payment
- Send reminder email
- Send SMS reminder
- Offer a discount
- Offer a grace period
- Mark promise to pay
- Escalate to a human agent
- Stop further recovery attempts

---

## ✅ Compliance & Safety Rules

Before performing any action, the system checks:

- Do Not Contact customers
- Customer opt-outs
- Active payment disputes
- Maximum contact attempts
- Maximum recovery window
- Quiet hours (disabled in demo mode)

These rules ensure recovery actions remain compliant.

---

## 📧 Real Email Integration

Recovery emails are sent using **Resend**.

The project supports:

- Real email delivery
- Personalized email templates
- Test recipient redirection for demo purposes

---

## 📊 Interactive Dashboard

The dashboard displays:

- Total revenue at risk
- Total recovered revenue
- Recovery rate
- Root cause analysis
- Recovery statistics
- Event history
- Complete audit trail

---

# 🏗️ System Architecture

```
Revenue Events
      │
      ▼
Detect At-Risk Events
      │
      ▼
AI Diagnosis
(OpenAI GPT-OSS-120B via Groq)
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
 ┌────┴───────────────┐
 │                    │
 ▼                    ▼
Send Email       Retry Payment
 │                    │
 └────────────┬───────┘
              ▼
Update Database
              │
              ▼
Dashboard & Audit Logs
```

---

# 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | SQLite + SQLAlchemy |
| AI Model | OpenAI GPT-OSS-120B (via Groq API) |
| Email Service | Resend |
| Deployment | Vercel + Render |

---

# ☁️ Deployment

## Frontend

- Hosted on **Vercel**
- Connected directly to GitHub
- Automatically redeploys whenever new code is pushed

**Live URL**

https://airevenue-recovery-project1.vercel.app/

---

## Backend

- Hosted on **Render**
- FastAPI application
- Connected directly to GitHub
- Automatically redeploys after every GitHub push

Configured environment variables:

```
GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-120b
RESEND_API_KEY
SEND_REAL_EMAILS
TEST_RECIPIENT_EMAIL
```

---

## Frontend Configuration

The frontend communicates with the deployed backend using:

```
VITE_API_BASE_URL=https://your-render-backend.onrender.com
```

---

## Deployment Workflow

```
           GitHub Repository
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
   Vercel Frontend     Render Backend
        │                   │
        │                   ▼
        │            SQLite Database
        │                   │
        │                   ▼
        │        OpenAI GPT-OSS-120B
        │          (via Groq API)
        │                   │
        │                   ▼
        │             Resend Email API
        └───────────────┬───────────────┘
                        ▼
                 User Dashboard
```

---

# 🚀 Running Locally

## Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

API Documentation:

```
http://localhost:8000/docs
```

---

## Frontend

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

# 🔐 Environment Variables

## Backend

```
GROQ_API_KEY=your_api_key

GROQ_MODEL=openai/gpt-oss-120b

RESEND_API_KEY=your_api_key

SEND_REAL_EMAILS=true

TEST_RECIPIENT_EMAIL=your_email@example.com
```

---

## Frontend

```
VITE_API_BASE_URL=http://localhost:8000
```

---

# 🔄 Demo Workflow

```
Seed Batch Data
        │
        ▼
Detect At-Risk Events
        │
        ▼
AI Root Cause Diagnosis
        │
        ▼
Decision Engine
        │
        ▼
Compliance Validation
        │
        ▼
Execute Recovery
        │
        ▼
Send Recovery Email
        │
        ▼
Update Database
        │
        ▼
Refresh Dashboard
        │
        ▼
Store Audit Logs
```

---

# 📂 Project Structure

```
ai-revenue-recovery/

├── backend/
│   ├── agent/
│   ├── api/
│   ├── rules/
│   ├── services/
│   ├── models/
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── api.ts
│   └── App.tsx
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEMO_SCRIPT.md
│
├── README.md
└── docker-compose.yml
```

---

# ✅ Current Implementation

| Feature | Status |
|----------|--------|
| AI Revenue Detection | ✅ |
| AI Root Cause Diagnosis | ✅ |
| Intelligent Decision Engine | ✅ |
| Compliance Rules | ✅ |
| Stopping Rules | ✅ |
| Real Email Sending | ✅ |
| Dashboard | ✅ |
| Audit Trail | ✅ |
| Synthetic Data Generator | ✅ |
| Deployment | ✅ |

---

# 🚀 Future Improvements

- Twilio SMS integration
- Stripe payment retry integration
- PostgreSQL database
- Multi-tenant architecture
- Real payment gateway webhooks
- Advanced analytics dashboard
- Authentication & role-based access

---

# 📸 Sample Workflow

1. Seed synthetic customer data.
2. Detect revenue at risk.
3. AI diagnoses the root cause.
4. Decision engine selects the best intervention.
5. Compliance rules validate the action.
6. Recovery email is sent.
7. Dashboard updates recovery metrics.
8. Every action is stored in the audit trail.

This project demonstrates how AI can automate revenue recovery while maintaining compliance, transparency, and complete traceability.
