# AgentOps Governance Platform

Enterprise reference architecture for governing agentic AI in regulated insurance claims workflows. The backend is implemented in `backend/` with FastAPI, SQLite, deterministic governance controls, and optional local Ollama support.

Run the API:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs.

