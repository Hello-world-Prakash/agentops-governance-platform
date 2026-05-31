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
