# GitHub Repository AI Assistant — React + FastAPI

Copy `api/` into your project root (next to `ui/`, `scripts/`, `retrieval/`, `llm/`)
and copy `frontend/` into the root as well.

## Run
Terminal 1 (project root):
    pip install fastapi "uvicorn[standard]"
    uvicorn api.main:app --reload --port 8000

Terminal 2:
    cd frontend
    npm install
    npm run dev        # http://localhost:5173
