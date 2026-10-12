"""
FastAPI backend for the GitHub Repository AI Assistant.

Place this folder (api/) in your project root, next to ui/, scripts/, retrieval/, llm/.
Run from the project root:  uvicorn api.main:app --reload --port 8000
"""
import json
import uuid
from typing import Any, Iterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from scripts.index_repository import ingest_repository
from retrieval.vector_retriever import VectorRetriever
from llm.llm_client import LLMClient
from llm.prompt_builder import PromptBuilder
from llm.answer_generator import AnswerGenerator

app = FastAPI(title="GitHub Repository AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (replaces st.session_state for server-side objects).
# repo_id -> {"generator": AnswerGenerator, "path": ..., "owner": ..., "name": ...}
REPOS: dict[str, dict[str, Any]] = {}


class IndexRequest(BaseModel):
    repo_url: str


class ChatRequest(BaseModel):
    repo_id: str
    question: str
    top_k: int = Field(5, ge=1, le=10)
    temperature: float = Field(0.2, ge=0.0, le=1.0)


def _line(event: dict) -> str:
    """One JSON object per line (NDJSON) so the frontend can read progress live."""
    return json.dumps(event) + "\n"


def _parse_owner_repo(repo_url: str) -> tuple[str, str]:
    clean_url = repo_url.strip().rstrip("/").removesuffix(".git")
    parts = clean_url.split("/")
    owner = parts[-2] if len(parts) >= 2 else "owner"
    name = parts[-1] if len(parts) >= 1 else "repo"
    return owner, name


def _normalize_source(src: dict, idx: int) -> dict:
    score = src.get("score", 0.90)
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0
    return {
        "file_path": src.get("file_path", f"file_{idx}.py"),
        "start_line": src.get("start_line", 1),
        "end_line": src.get("end_line", 20),
        "match_pct": int(score * 100) if score <= 1.0 else int(score),
        "content": src.get("content", ""),
        "language": src.get("language", "python"),
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/repos/index")
def index_repo(req: IndexRequest) -> StreamingResponse:
    repo_url = req.repo_url.strip()
    if not repo_url:
        raise HTTPException(status_code=400, detail="Please enter a valid GitHub repository URL.")

    def stream() -> Iterator[str]:
        try:
            yield _line({"type": "step", "step": 1, "message": "Cloning repository, parsing & chunking..."})
            repo_path, docs, chunks = ingest_repository(repo_url)

            yield _line({"type": "step", "step": 2, "message": "Loading FAISS vector index..."})
            owner, name = _parse_owner_repo(repo_url)
            retriever = VectorRetriever(repo_path)

            yield _line({"type": "step", "step": 3, "message": "Initialising Gemini answer generator..."})
            generator = AnswerGenerator(retriever, PromptBuilder(), LLMClient())

            languages = {getattr(d, "language", "unknown") for d in docs}
            file_paths = sorted(getattr(d, "file_path", f"File #{i}") for i, d in enumerate(docs))

            repo_id = uuid.uuid4().hex[:12]
            REPOS[repo_id] = {
                "generator": generator,
                "path": str(repo_path),
                "owner": owner,
                "name": name,
            }

            yield _line({
                "type": "done",
                "repo": {
                    "repo_id": repo_id,
                    "owner": owner,
                    "name": name,
                    "stats": {
                        "files": len(docs),
                        "chunks": len(chunks),
                        "languages": len(languages),
                    },
                    "file_paths": file_paths,
                },
            })
        except Exception as e:  # surfaced in the UI like st.error
            yield _line({"type": "error", "message": f"Indexing Error: {e}"})

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    repo = REPOS.get(req.repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found. Please index it again.")

    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")

    try:
        result = repo["generator"].answer_question(
            question=question,
            top_k=req.top_k,
            temperature=req.temperature,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    sources = [_normalize_source(s, i) for i, s in enumerate(result.get("sources", []))]
    return {"answer": result.get("answer", ""), "sources": sources}
