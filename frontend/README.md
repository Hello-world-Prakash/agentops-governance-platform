# Frontend

Next.js, React, and TypeScript dashboard for the AgentOps Governance Platform.

## Run

```powershell
cd frontend
npm install
npm run dev
```

The dashboard expects the FastAPI backend at `http://127.0.0.1:8000`.
Override it with:

```powershell
$env:NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
```

## Auth.js / OAuth / SSO

Auth.js protection is enabled by default. The app includes a local `Demo SSO` credentials provider so the dashboard can be tested without OAuth credentials.

Default local login:

```text
Provider: Demo SSO
Email: demo.admin@agentops.local
Role: Admin
```

Disable auth only for local demos:

```powershell
$env:NEXT_PUBLIC_AUTH_REQUIRED="false"
npm run dev
```

PowerShell example for GitHub OAuth:

```powershell
$env:AUTH_SECRET="replace-with-generated-secret"
$env:AUTH_GITHUB_ID="replace-with-github-oauth-client-id"
$env:AUTH_GITHUB_SECRET="replace-with-github-oauth-client-secret"
$env:NEXT_PUBLIC_AUTH_REQUIRED="true"
$env:AUTH_DEMO_LOGIN="false"
npm run dev
```

When `NEXT_PUBLIC_AUTH_REQUIRED` is not `false`, the proxy protects dashboard routes and redirects unauthenticated users to `/api/auth/signin`. The same Auth.js setup can be extended later with enterprise SSO providers such as Azure AD / Microsoft Entra ID, Okta, Auth0, or any OIDC-compatible identity provider.

## Role-Based Access Control

RBAC is implemented in `lib/rbac.ts` and applied in the dashboard UI. Local demo mode defaults to `Admin` so the full reference workflow remains easy to test.

Override the local demo role:

```powershell
$env:NEXT_PUBLIC_DEMO_ROLE="Auditor"
npm run dev
```

Role matrix:

| Role | Permissions |
| --- | --- |
| Admin | Manage policies, users, agents, claims, high-risk approvals, and audit logs |
| Claims Adjuster | Submit and review claims |
| Risk Reviewer | Review claims, approve or reject high-risk decisions, and inspect audit evidence |
| Auditor | View audit logs only |
| Read-only Viewer | View dashboard posture only |

For SSO, Auth.js reads platform roles from common claims such as `role`, `roles`, `groups`, or `https://agentops.example.com/roles`. Set `AUTH_DEFAULT_ROLE` as a fallback for users whose provider profile does not contain a mapped role.

## Approval History

The approval view shows pending, approved, rejected, and manual-review items. Approve, reject, and manual-review decisions require a reviewer comment before the API request is sent.

Default comment examples:

- Approval reason: `Evidence is complete and risk is low.`
- Rejection reason: `Missing repair estimate and police report.`
- Manual review reason: `Conflicting policy evidence.`
