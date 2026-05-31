from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agents, approvals, audit_logs, claims, policies
from app.database.db import Base, engine
from app.database.migrations import ensure_sqlite_approval_columns


Base.metadata.create_all(bind=engine)
ensure_sqlite_approval_columns()

app = FastAPI(title="AgentOps Governance Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims.router)
app.include_router(agents.router)
app.include_router(approvals.router)
app.include_router(audit_logs.router)
app.include_router(policies.router)


@app.get("/health")
def health():
    return {"status": "ok"}
