"""
FastAPI backend for the Medical RAG System.
Wraps the existing src/ pipeline (document_loader, embeddings_manager,
rag_pipeline, evaluation) behind a small HTTP API for the React frontend.
"""
import sys
import os
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Make src/ importable, same trick main.py uses
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from config import GOOGLE_API_KEY, DOCUMENTS_DIR, TOP_K  # noqa: E402
from document_loader import prepare_documents  # noqa: E402
from embeddings_manager import initialize_embeddings, EmbeddingsManager  # noqa: E402
from rag_pipeline import create_rag_pipeline, RAGPipeline  # noqa: E402
from evaluation import RAGEvaluator  # noqa: E402


# ---------------------------------------------------------------------------
# App state (populated on startup)
# ---------------------------------------------------------------------------
class AppState:
    embeddings_manager: Optional[EmbeddingsManager] = None
    rag_pipeline: Optional[RAGPipeline] = None
    evaluator: Optional[RAGEvaluator] = None
    document_count: int = 0
    source_files: List[str] = []
    ready: bool = False
    init_error: Optional[str] = None


state = AppState()

app = FastAPI(title="Medical RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    """Load documents, build the vector store, and stand up the RAG pipeline."""
    try:
        documents = prepare_documents()
        if not documents:
            state.init_error = "No documents found in the documents/ directory."
            return

        state.document_count = len(documents)
        state.source_files = sorted({d.metadata.get("source", "unknown") for d in documents})

        state.embeddings_manager = initialize_embeddings(documents)

        if not GOOGLE_API_KEY:
            state.init_error = "GOOGLE_API_KEY not set. Retrieval works, generation will fail."
            return

        state.rag_pipeline = create_rag_pipeline(state.embeddings_manager)
        state.evaluator = RAGEvaluator()
        state.ready = True
    except Exception as e:  # noqa: BLE001
        state.init_error = str(e)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str


class SourceChunk(BaseModel):
    source: str
    snippet: str
    metadata: dict


class QueryResponse(BaseModel):
    response: str
    sources: List[SourceChunk]
    latency_ms: int
    mode: str


class HistoryEntry(BaseModel):
    query: str
    response: str
    sources: List[str]
    mode: Optional[str] = "grounded"


class EvalRequest(BaseModel):
    query: Optional[str] = None
    response: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {
        "ready": state.ready,
        "document_count": state.document_count,
        "source_files": state.source_files,
        "error": state.init_error,
    }


@app.get("/api/documents")
def documents():
    return {
        "document_count": state.document_count,
        "sources": state.source_files,
        "top_k": TOP_K,
    }


@app.post("/api/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not state.rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail=state.init_error or "RAG pipeline is not ready yet.",
        )
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    start = time.time()
    result = state.rag_pipeline.generate_response(req.query)
    latency_ms = int((time.time() - start) * 1000)

    retrieved = result.get("documents", [])
    sources = [
        SourceChunk(
            source=doc.metadata.get("source", "Unknown"),
            snippet=doc.page_content[:220].strip(),
            metadata={
                k: v
                for k, v in doc.metadata.items()
                if k in ("medical_specialty", "sample_name", "keywords", "source", "page")
            },
        )
        for doc in retrieved
    ]

    return QueryResponse(
        response=result["response"],
        sources=sources,
        latency_ms=latency_ms,
        mode=result.get("mode", "grounded"),
    )


@app.get("/api/history", response_model=List[HistoryEntry])
def history():
    if not state.rag_pipeline:
        return []
    return state.rag_pipeline.get_conversation_history()


@app.delete("/api/history")
def clear_history():
    if state.rag_pipeline:
        state.rag_pipeline.conversation_history = []
    return {"status": "cleared"}


@app.post("/api/eval")
def evaluate(req: EvalRequest):
    if not state.evaluator:
        raise HTTPException(status_code=503, detail="Evaluator is not ready yet.")

    query_text, response_text = req.query, req.response
    if not query_text or not response_text:
        if not state.rag_pipeline or not state.rag_pipeline.get_conversation_history():
            raise HTTPException(status_code=400, detail="No conversation to evaluate yet.")
        last = state.rag_pipeline.get_conversation_history()[-1]
        query_text, response_text = last["query"], last["response"]

    result = state.evaluator.evaluate_response(query=query_text, response=response_text)
    if result.get("status") != "success":
        raise HTTPException(status_code=502, detail=result.get("error", "Evaluation failed."))
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
