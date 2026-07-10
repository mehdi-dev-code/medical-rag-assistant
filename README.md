# Medical RAG System

A full-stack Retrieval-Augmented Generation (RAG) system for medical Q&A —
FastAPI + React frontend on top of a Google Gemini + local HuggingFace
embeddings pipeline, with a hybrid grounded/general answering mode.

## 🎯 What This Project Does

This is a **working AI system that combines:**
- ✅ **Document Processing** - Load and chunk medical documents (TXT, PDF, or CSV)
- ✅ **Vector Embeddings** - HuggingFace embeddings (local, no API needed)
- ✅ **Semantic Search** - FAISS vector store for efficient retrieval
- ✅ **RAG Pipeline** - Retrieve relevant documents → Generate contextual responses
- ✅ **Hybrid Answering** - Uses your documents when relevant; falls back to
  Gemini's own general medical knowledge (clearly labeled) when they're not
- ✅ **LLM Integration** - Gemini API for response generation
- ✅ **Evaluation Framework** - Test response quality
- ✅ **REST API** - FastAPI backend exposing the pipeline over HTTP
- ✅ **Web UI** - React frontend with a live retrieval-trace visualization
- ✅ **Production Patterns** - Clean architecture, error handling, logging

## 🏗️ Architecture

\`\`\`
React Frontend (Vite, :5173)
    ↓  HTTP (/api/*)
FastAPI Backend (:8000)
    ↓
User Question
    ↓
HuggingFace Embeddings (local)
    ↓
FAISS Vector Search → Find relevant medical documents
    ↓
RAG Pipeline → Format context, decide GROUNDED vs GENERAL mode
    ↓
Google Gemini LLM → Generate medical response
    ↓
Evaluation Framework → Assess response quality (on demand)
\`\`\`

**Hybrid mode, in short:** every response is tagged by the model itself as
either grounded in your documents or answered from its own general medical
knowledge. When nothing relevant is retrieved, the UI shows an honest
"general medical knowledge — not from your documents" badge instead of
pretending irrelevant chunks were the source.

## 🚀 Quick Start

### Step 1: Get a Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Create API Key"**
3. Copy the key

### Step 2: Configure Environment
In the project root:
1. Copy `.env.example` to `.env`:
   \`\`\`bash
   copy .env.example .env
   \`\`\`
2. Edit `.env` and paste your key:
   \`\`\`
   GOOGLE_API_KEY=your-actual-key-here
   \`\`\`

### Step 3: Install Backend Dependencies
From the project root:
\`\`\`bash
pip install -r backend/requirements.txt
\`\`\`
This installs the original RAG stack (langchain, faiss, sentence-transformers,
etc.) plus FastAPI/uvicorn/pydantic in one shot — `backend/requirements.txt`
references the root `requirements.txt` internally.

### Step 4: Add Medical Documents
Place your medical documents in the `documents/` folder:
- Formats: `.txt`, `.pdf`, or `.csv`
- Examples: `diabetes_guide.txt`, `hypertension_guide.pdf`, etc.

### Step 5: Run the Backend
\`\`\`bash
cd backend
uvicorn app:app --reload --port 8000
\`\`\`
On startup it loads `documents/`, builds the FAISS index, and stands up the
pipeline. Check `http://localhost:8000/api/health` — it should report
`"ready": true` once indexing finishes.

### Step 6: Run the Frontend
In a second terminal:
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`
Open `http://localhost:5173`. The dev server proxies `/api/*` to
`http://localhost:8000` automatically.

### (Optional) CLI mode
The original terminal interface still works independently of the web stack:
\`\`\`bash
python main.py
\`\`\`

## 💬 Using the System

**Web UI** (`http://localhost:5173`):
- Ask a question in the chat box
- Grounded answers show source-document chips and a live retrieval trace
- Out-of-scope questions show a "general medical knowledge" badge instead
- "Evaluate this response" scores the last answer on accuracy/clarity/completeness/safety

**CLI** (`python main.py`):
\`\`\`
👤 You: What are the symptoms of diabetes?
🤖 Assistant: [Response with source documents]
\`\`\`
Commands: type a question, or `history`, `eval`, `exit`.

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `langchain` | LLM orchestration |
| `langchain-google-genai` | Gemini API integration |
| `sentence-transformers` | HuggingFace embeddings |
| `faiss-cpu` | Vector search engine |
| `pypdf` | PDF processing |
| `python-dotenv` | Environment configuration |
| `fastapi` / `uvicorn` | REST API + server (backend) |
| `react` / `vite` | Web UI (frontend) |
| `react-markdown` / `remark-gfm` | Renders Gemini's Markdown responses |

## 📁 Project Structure

'''
medical-rag-fullstack/
├── main.py                    # CLI entry point
├── requirements.txt            # Core Python dependencies
├── .env.example                # Configuration template
├── .env                        # Your API key (create this)
├── documents/                  # Add your medical documents here
├── embeddings/                 # Vector store (auto-created)
├── src/
│   ├── config.py                # Configuration + system prompt
│   ├── document_loader.py        # Document loading & chunking
│   ├── embeddings_manager.py     # Embedding & vector store
│   ├── rag_pipeline.py          # RAG logic + grounded/general mode parsing
│   └── evaluation.py            # Response evaluation
├── backend/
│   ├── app.py                   # FastAPI wrapper around src/
│   └── requirements.txt          # Backend-only deps (references ../requirements.txt)
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Layout + state
│   │   ├── api.js                # Backend API client
│   │   ├── components/
│   │   │   ├── Sidebar.jsx        # Status + knowledge base list
│   │   │   ├── ChatThread.jsx      # Message list
│   │   │   ├── MessageBubble.jsx   # Markdown rendering, source/general badges
│   │   │   ├── ChatInput.jsx       # Input bar
│   │   │   └── RetrievalTrace.jsx  # Live retrieval visualization + eval
│   │   └── styles/                # Design tokens + component styles
│   └── package.json
└── RUNNING_THE_APP.md          # Detailed run instructions
'''

## ⚙️ Key Features

### 1. Local Embeddings
- Uses HuggingFace `sentence-transformers`
- Runs completely locally (no API calls)
- Fast and reliable
- Model: `all-MiniLM-L6-v2` (lightweight)

### 2. Document Processing
- Automatic chunking with overlap (1000 chars, 200 overlap)
- Support for TXT, PDF, and CSV files
- Metadata preservation for source tracking

### 3. Vector Search
- FAISS index for efficient retrieval
- Top-K document retrieval (configurable)
- Persistent storage on disk

### 4. Hybrid RAG Pipeline
- Multi-step: retrieve → format → generate → self-tag mode
- The model tags its own response `MODE: GROUNDED` or `MODE: GENERAL`
  depending on whether the retrieved chunks were actually relevant
- The API and UI use that tag to avoid presenting irrelevant chunks as
  if they were real sources
- System prompts for safety, conversation history tracking

### 5. Gemini Integration
- Uses `gemini-2.5-flash` (fast, cost-effective)
- Temperature control for consistency
- Token limits respected

### 6. Web Interface
- FastAPI REST API (`/api/query`, `/api/health`, `/api/history`, `/api/eval`, `/api/documents`)
- React frontend with a dark, clinical-tech visual style
- Retrieval trace panel: retrieved chunks animate in as a live pulse-line,
  or show an honest "no relevant documents" state in general mode
- Markdown rendering for headings/bold/lists/tables in Gemini's responses

## 🔧 Configuration

Edit `src/config.py` to customize:
- `CHUNK_SIZE`: Document chunk size (default: 1000)
- `CHUNK_OVERLAP`: Chunk overlap (default: 200)
- `TOP_K`: Documents to retrieve (default: 3)
- `MODEL_NAME`: Gemini model to use
- `EMBEDDING_MODEL`: HuggingFace model
- `SYSTEM_PROMPT`: Controls the grounded/general mode-tagging behavior

Edit `backend/app.py`'s `allow_origins` before deploying anywhere beyond
`localhost:5173`.

## 📝 Example Medical Documents

Create sample documents in `documents/`:

**diabetes_guide.txt:**
\`\`\`
Diabetes Type 2

Symptoms:
- Increased thirst
- Frequent urination
- Unexplained weight loss
- Fatigue
- Blurred vision

Management:
- Healthy diet
- Regular exercise
- Blood sugar monitoring
- Medication if needed
\`\`\`

## 🐛 Troubleshooting

**"GOOGLE_API_KEY not found" / "API key not valid"**
- Make sure `.env` exists in the project root with a valid key
- If you change the key while `uvicorn` is already running, `--reload`
  will **not** pick it up — the Gemini client is built once at startup.
  Fully stop the process (check `netstat -ano | findstr :8000` on Windows
  for a stale process still holding the port) and restart `uvicorn` fresh.

**"No documents found"**
- Add `.txt`, `.pdf`, or `.csv` files to `documents/`
- Restart the backend

**Sidebar stuck on "Initializing…"**
- Check `http://localhost:8000/api/health` directly — if it errors or never
  loads, the backend isn't running or crashed during startup; check its
  terminal output

**Slow embeddings on first run**
- First run downloads the embedding model (~200MB)
- Subsequent runs are much faster

**Dependency conflicts after installing backend requirements**
- `protobuf` has no upper bound pin in `requirements.txt`; if pip grabs a
  version too new for `google-ai-generativelanguage`, run:
  \`\`\`
  pip install "protobuf<5.0.0,>=4.25.0"
  \`\`\`

## 📊 Performance

- Document loading: < 1 second
- Embedding creation: ~5 seconds per 20 documents
- Query retrieval: < 100ms
- Response generation: 2-5 seconds (depends on Gemini API)

## 📝 License

MIT License

## 👤 Author

Mehdi Ali