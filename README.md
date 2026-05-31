# AgentOps Governance Platform

This is not a chatbot.

AgentOps Governance Platform is an AgentOps governance control plane for regulated enterprise AI workflows. It demonstrates how insurance claims agents can extract facts, retrieve policy evidence, assess fraud risk, and recommend decisions while every sensitive action is routed through deterministic governance, policy enforcement, risk scoring, approval workflows, PII masking, and audit logging.

## Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.svg)

### Claim Review
![Claim Review](docs/screenshots/claim-review.svg)

### Audit Logs
![Audit Logs](docs/screenshots/audit-logs.svg)

### Approval Queue
![Approval Queue](docs/screenshots/approval-queue.svg)

### Evaluation Center
![Evaluation Center](docs/screenshots/evaluation-center.svg)

### Red Team Scenarios
![Red Team Scenarios](docs/screenshots/red-team-scenarios.svg)

### Trace Timeline
![Trace Timeline](docs/screenshots/trace-timeline.svg)

### Policy Rules
![Policy Rules](docs/screenshots/policy-rules.svg)

### Login/Auth
![Login/Auth](docs/screenshots/login-auth.svg)

## Architecture

- FastAPI backend
- Next.js, React, and TypeScript frontend
- PostgreSQL-backed audit and approval persistence in Docker Compose
- SQLite fallback for lightweight local tests
- Redis event bus for trace and approval events
- SSE real-time trace streaming
- Local Ollama/Llama support for extraction summaries and reasoning explanations only
- LangGraph-compatible claim workflow orchestration with deterministic fallback
- Auth.js / OAuth / future SSO scaffold
- Role-based access control
- Deterministic governance gateway
- Prompt-injection detector
- PII detector and audit-log masking
- Human approval queue with decision history
- Trace timeline pages for audit evidence

## Governance Rules

- Prompt injection is blocked.
- Claim denial requires human approval.
- High claim amount approval recommendations require human approval.
- Low confidence requires manual review.
- High fraud score requires manual review.
- PII is masked before audit logs are saved.
- LLM output is never the source of truth for final approval, final denial, risk scoring, prompt-injection blocking, or audit logging.

## Run Locally

Backend:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

- Backend docs: http://127.0.0.1:8000/docs
- Frontend dashboard: http://127.0.0.1:3000

## Docker Compose

```powershell
docker compose up --build
```

Services:

- `backend`
- `frontend`
- `database` using PostgreSQL
- `redis`

Later-ready services are documented in `docker-compose.yml` as placeholders:

- `ollama`

## Architecture Diagram

```mermaid
flowchart LR
    U["Enterprise User"] --> F["Next.js Dashboard"]
    F --> A["Auth.js / OAuth / SSO"]
    F --> B["FastAPI Governance API"]
    B --> O["LangGraph-compatible Workflow"]
    O --> I["Claims Intake Agent"]
    O --> P["Policy Retrieval Agent"]
    O --> R["Fraud Risk Agent"]
    O --> D["Claim Decision Agent"]
    D --> G["Governance Gateway"]
    G --> PI["Prompt Injection Detector"]
    G --> RS["Risk Scorer"]
    G --> PE["Policy Engine"]
    G --> PM["PII Masking"]
    PM --> PG["PostgreSQL Audit Store"]
    G --> Q["Human Approval Queue"]
    B --> RE["Redis Event Bus"]
    RE --> TS["SSE Trace Streaming"]
    F --> TS
    O -. summaries/explanations only .-> L["Ollama / Llama"]
```

## Trace Timeline

Audit log rows link to `/traces/[trace_id]`. Each trace page fetches `GET /audit-logs/{trace_id}` and displays:

- user request
- agent output
- retrieved evidence
- risk score
- governance decision
- policy reasons
- approval status
- final status

## Approval Queue

The approval queue shows:

- pending approvals
- approved approvals
- rejected approvals
- manual-review items
- reviewer identity
- decision timestamp
- required decision reason/comment

Example decision comment:

```json
{
  "reviewer_name": "Risk Reviewer",
  "decision_comment": "Evidence is complete and risk is low."
}
```
