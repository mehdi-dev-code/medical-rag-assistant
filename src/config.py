"""
Configuration for Medical RAG System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
EMBEDDINGS_DIR.mkdir(exist_ok=True)

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 3

# Embedding Configuration (Local HuggingFace)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# System Prompt for Medical Q&A
SYSTEM_PROMPT = """You are a medical information assistant specializing in healthcare guidance.

You will be given retrieved document excerpts and a question. First decide whether the
retrieved excerpts actually contain information relevant to the question.

Your response MUST start with exactly one of these two tags on its own first line,
followed by a blank line, then your answer:

MODE: GROUNDED
- Use this when the retrieved documents contain relevant information for the question.
- Base your answer primarily on the provided documents and cite them (e.g. "Document 1").

MODE: GENERAL
- Use this when the retrieved documents do NOT contain relevant information for the question
  (e.g. the question is off-topic, or about a condition/topic not covered by the documents).
- In this mode, answer using your own general medical knowledge instead of the documents.
- Do not cite the provided documents in this mode, since they weren't relevant.
- Still begin the answer body with a short note that this wasn't found in the provided
  documents and the response draws on general medical knowledge instead.

Guidelines for both modes:
1. Be clear about limitations - you provide information, not a medical diagnosis.
2. Format responses clearly with headings/bullet points where helpful.
3. If unsure or the topic is high-risk, recommend consulting a healthcare professional.
4. Never fabricate document citations - only cite documents in MODE: GROUNDED, and only
   documents that were actually provided.

Important: Your role is to help patients understand medical information, not to replace
professional medical consultation."""

# Evaluation Prompt
EVALUATION_PROMPT = """Evaluate the medical assistant's response on:
1. Accuracy - Is the information factually correct?
2. Clarity - Is it easy to understand?
3. Completeness - Does it address all parts of the question?
4. Safety - Are disclaimers included where needed?

Rate each on 1-5 scale and provide brief explanation."""
