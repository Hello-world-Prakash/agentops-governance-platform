# API Contract

Primary workflow endpoint: `POST /claims/review`.

Operational endpoints: `GET /agents`, `GET /approvals`, `GET /approvals/pending`, approval action endpoints, `GET /audit-logs`, `GET /policies`, and `POST /policies/evaluate`.

Approval action endpoints require a reviewer and decision comment:

```json
{
  "reviewer_name": "Risk Reviewer",
  "decision_comment": "Evidence is complete and risk is low."
}
```

Approval records include `status`, `created_at`, `decided_at`, `reviewer_name`, and `decision_comment` so the dashboard can show pending approvals, approved approvals, rejected approvals, and manual-review items.
