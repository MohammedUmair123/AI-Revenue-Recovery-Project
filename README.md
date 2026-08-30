# AI Revenue Recovery Agent

Detects revenue at risk (failed payments, abandoned checkouts, failed
subscription renewals, overdue B2B invoices), diagnoses the root cause with
an LLM, decides the right intervention, and executes a **bounded** recovery
workflow — with compliance gates, stopping rules, and a full audit trail.

See `docs/ARCHITECTURE.md` for the pipeline design and `docs/DEMO_SCRIPT.md`
for a walkthrough script.

## Stack (100% free tier)

- **LLM**: [Groq](https://console.groq.com) — free API, Llama 3.3 70B
- **Backend**: FastAPI + SQLite
- **Frontend**: React + Vite + Tailwind
- **Email**: [Resend](https://resend.com) — free tier, 100 emails/day (or run fully simulated/logged)
- **Deploy**: Render or Railway (backend, free tier) + Vercel (frontend, free tier)

## Local setup (VS Code)

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add your free GROQ_API_KEY from https://console.groq.com
# (Resend key optional — leave SEND_REAL_EMAILS=false to run fully simulated)
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 3. Try it

1. Open `http://localhost:5173`
2. Click **Seed Batch Data** — generates ~120 synthetic at-risk events
3. Click **Run Recovery Batch** — runs the full detect → diagnose → decide →
   act pipeline and shows measured $ recovered, by root cause, plus the audit
   trail

Or drive it directly:

```bash
curl -X POST "http://localhost:8000/api/seed?n_customers=40&n_events=120"
curl -X POST "http://localhost:8000/api/run-batch"
curl "http://localhost:8000/api/metrics"
```

## Testing real email sends

Resend has two sandbox restrictions until you verify a domain at resend.com/domains:
- You can only send **from** `onboarding@resend.dev` (not a custom or Gmail address).
- You can only send **to** the email address you signed up to Resend with.

Since our seed data generates fake customer emails, set `TEST_RECIPIENT_EMAIL` in
`backend/.env` to your real Resend signup address — every real send gets redirected
there (with the original fake customer address noted in the subject line), so you
can actually watch an email land in your inbox without changing any recovery logic.
Leave it blank once you verify your own domain in production.

## Getting free API keys

- **Groq** (LLM, required for real diagnosis — falls back to rule-based
  classification if unset): https://console.groq.com → API Keys → Create.
- **Resend** (real email sending, optional — simulated/logged by default):
  https://resend.com → sign up free, no card required → API Keys.

## Deployment (free tier)

### Backend → Render
1. Push this repo to GitHub.
2. On [Render](https://render.com), New → Blueprint → point at the repo
   (`backend/render.yaml` is already set up).
3. Add `GROQ_API_KEY` (and `RESEND_API_KEY` if using real email) as secret
   env vars in the Render dashboard.
4. Deploy. Note the public URL, e.g. `https://ai-revenue-recovery-backend.onrender.com`.

*(Railway works the same way — New Project → Deploy from GitHub, uses the
same `Dockerfile`.)*

### Frontend → Vercel
1. On [Vercel](https://vercel.com), New Project → import the repo, set root
   directory to `frontend`.
2. Add env var `VITE_API_BASE_URL` = your Render backend URL.
3. Deploy.

## Project structure

```
ai-revenue-recovery/
├── backend/            FastAPI app: agent pipeline, rules, API, DB
├── frontend/            React dashboard: ledger, event table, audit trail
├── docs/                 Architecture + demo script
├── docker-compose.yml   Local dev: run both services together
└── README.md
```

## What's simulated vs. real in this scaffold

| Part | Status |
|---|---|
| Root-cause diagnosis | Real LLM call (Groq), with rule-based fallback |
| Compliance & stopping rules | Real, enforced logic |
| Email sending | Real (Resend) if `SEND_REAL_EMAILS=true`, otherwise logged |
| SMS sending | Simulated/logged (swap in Twilio/MSG91 for production) |
| Payment retry | Simulated success probability (swap in real gateway call) |
| Audit trail | Real, persisted, append-only |
| Data | Synthetic (Faker) — swap `seed_data.py` for a real webhook ingester |
