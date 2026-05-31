# Architecture

The platform routes insurance claim agent recommendations through a central governance gateway. Agents produce facts, policy evidence, fraud indicators, and recommendations. The gateway applies deterministic prompt-injection detection, policy rules, risk scoring, PII masking, approval routing, and audit logging before any downstream action can proceed.

```mermaid
flowchart TD
    claim["Claim Review Request"] --> graph["LangGraph-compatible workflow"]
    graph --> intake["Claims Intake Agent"]
    graph --> policy["Policy Retrieval Agent"]
    graph --> fraud["Fraud Risk Agent"]
    graph --> decision["Claim Decision Agent"]
    decision --> gateway["Governance Gateway"]
    gateway --> injection["Prompt Injection Detector"]
    gateway --> risk["Risk Scorer"]
    gateway --> rules["Policy Engine"]
    gateway --> pii["PII Detector + Masker"]
    pii --> audit["PostgreSQL Audit Logs"]
    gateway --> approvals["Approval Queue"]
    approvals --> redis["Redis Events"]
    audit --> redis
    redis --> sse["SSE Trace Stream"]
    sse --> ui["Next.js Dashboard"]
```

PostgreSQL is the production persistence target in Docker Compose. SQLite remains available as a local fallback when `DATABASE_URL` is not provided. Redis carries trace and approval events for real-time SSE consumers.
