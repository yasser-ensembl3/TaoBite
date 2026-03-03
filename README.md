# Tao Bite

PDF-based knowledge management system with RAG (Retrieval Augmented Generation). Upload PDFs or Markdown documents, build vector embeddings in Qdrant, and generate custom content (quotes, posts, summaries, insights) using Claude AI with anti-hallucination controls.

## What It Does

```
Documents (.md from Google Drive or .pdf uploads)
    │
    ├── PDF extraction: pdfplumber (primary) → LlamaParse (fallback)
    ├── Chunking: RecursiveCharacterTextSplitter (1000 tokens, 200 overlap)
    ├── Embeddings: OpenAI text-embedding-3-small (1536 dimensions)
    └── Storage: Qdrant vector database (collection: pdf_documents)
    │
    ▼
RAG Content Generation
    │
    ├── Semantic search: query → embedding → Qdrant similarity search
    ├── Relevance filtering: score threshold (default 30%)
    ├── Context assembly: top-k passages with source attribution
    └── Generation: Claude 3 Haiku with anti-hallucination prompting
    │
    ▼
Output: Generated content + source chunks with relevance scores
```

## Architecture

```
Tao Bite/
├── app.py                             # Main Flask application (30+ endpoints)
├── qdrant_store.py                    # Standalone Qdrant wrapper class
├── migrate_to_qdrant_cloud.py         # Local → Qdrant Cloud migration
├── obsidian_pdf_converter.py          # PDF → Obsidian Markdown converter
├── pdf_to_markdown.py                 # Marker-based PDF converter
├── templates/
│   ├── index.html                     # Main UI (content generator + DB overview)
│   ├── admin.html                     # Document upload page
│   ├── database_overview.html         # Database viewer
│   ├── draft_generator.html           # Substack draft generator
│   ├── qdrant_viewer.html             # Qdrant collection viewer
│   └── obsidian_converter.html        # Obsidian converter UI
├── static/
│   ├── css/                           # Stylesheets
│   └── js/                            # Client-side scripts
├── uploads/                           # Uploaded PDFs (gitignored)
├── outputs/                           # Converted Markdown (gitignored)
├── qdrant_storage/                    # Local vector DB (gitignored)
├── requirements.txt
└── .env.example
```

## Data Ingestion Pipeline

### From Google Drive (Markdown files)

Source documents are stored as `.md` files in Google Drive:
https://drive.google.com/drive/u/0/folders/1m874HrsS4DO7v9Y4pI4ES1sF2g4ktUlq

Download the `.md` files, then process them through the app's upload and auto-pipeline endpoints, or use the admin UI to upload and auto-process.

### From PDF Upload

1. **Upload** — POST `/upload` or drag-and-drop via `/admin` UI
2. **Extract** — Dual strategy: pdfplumber (local, fast, free) → LlamaParse fallback (cloud, OCR)
3. **Quality gate** — Minimum 100 characters extracted
4. **Chunk** — `RecursiveCharacterTextSplitter` (1000 tokens, 200 overlap, paragraph-aware)
5. **Embed** — OpenAI `text-embedding-3-small` (1536 dimensions, batch size 100)
6. **Store** — Upsert into Qdrant collection `pdf_documents` (cosine similarity)

Auto-pipeline: POST `/auto-pipeline/<job_id>` runs steps 3-6 automatically after upload.

## RAG Content Generation

1. User enters keywords + custom instructions (or picks a template)
2. Query embedded via OpenAI → semantic search in Qdrant (top_k passages, configurable 5-20)
3. Results filtered by relevance score (minimum 30%)
4. Context assembled with source attribution
5. Claude 3 Haiku generates content with strict anti-hallucination rules:
   - Word-for-word extraction only, no paraphrasing
   - Source citations required
   - Refuses if insufficient relevant content
   - Substantive quotes only (15+ words)
6. Response includes: generated content + source chunks with relevance scores

**Templates:** Quotes, LinkedIn Post, Summary, Key Terms, Insights — or custom instructions.

## Qdrant Database Setup

The Qdrant database needs to be created before ingesting documents. The app auto-creates the collection on first injection, but the Qdrant instance must be running.

### Option A: Local Qdrant (development)

No setup needed — the app uses local file-based storage (`./qdrant_storage/`) when no cloud URL is configured. The Qdrant client stores data in SQLite locally.

### Option B: Qdrant Cloud (production)

1. Create a free cluster at [cloud.qdrant.io](https://cloud.qdrant.io/)
2. Copy the cluster URL and API key
3. Set in `.env`:
   ```bash
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your-api-key
   ```

### Collection Schema

The app automatically creates the collection `pdf_documents` on first document injection:

```
Collection: pdf_documents
├── Vector size: 1536 (OpenAI text-embedding-3-small)
├── Distance metric: Cosine
└── Payload per point:
    ├── text: string          # Chunk content
    ├── chunk_id: int         # Sequential chunk number
    ├── token_count: int      # Token count (tiktoken)
    ├── char_count: int       # Character count
    ├── filename: string      # Source document name
    ├── job_id: string        # Processing job UUID
    └── source: string        # "pdfplumber" or "llamaparse"
```

### Recreating the Database

If the Qdrant database was deleted, re-ingest all documents:

1. Download all `.md` files from the Google Drive folder
2. Start the app (`python app.py`)
3. Upload each document via the `/admin` page — the auto-pipeline will:
   - Chunk the content
   - Generate OpenAI embeddings
   - Create the `pdf_documents` collection (auto)
   - Inject all vectors with metadata

The collection is created automatically by `ensure_qdrant_collection()` on first injection with:
- Vector size: 1536
- Distance: Cosine

### Migrating Local → Cloud

```bash
python migrate_to_qdrant_cloud.py
```

Transfers all vectors from `./qdrant_storage/` to Qdrant Cloud in batches.

## API Routes

### Content Generation
| Route | Method | Description |
|-------|--------|-------------|
| `/generate-content` | POST | Generate content with keywords + custom instructions |
| `/extract-quotes` | POST | Extract quotes (legacy) |
| `/generate-draft` | POST | Generate Substack drafts |

### Document Management
| Route | Method | Description |
|-------|--------|-------------|
| `/upload` | POST | Upload PDF |
| `/auto-pipeline/<job_id>` | POST | Auto-process: chunk → embed → inject |
| `/status/<job_id>` | GET | Check processing status |

### Database
| Route | Method | Description |
|-------|--------|-------------|
| `/api/database/stats` | GET | Collection statistics |
| `/api/database/documents` | GET | List all documents with metadata |
| `/qdrant/search` | POST | Semantic search |

## Setup

### Prerequisites

- Python 3.11+
- API keys: OpenAI, Anthropic (required), LlamaParse (optional)

### Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | Embeddings (text-embedding-3-small) |
| `ANTHROPIC_API_KEY` | Yes | Claude 3 Haiku content generation |
| `LLAMA_CLOUD_API_KEY` | No | LlamaParse PDF fallback extraction |
| `QDRANT_URL` | No | Qdrant Cloud URL (local storage if unset) |
| `QDRANT_API_KEY` | No | Qdrant Cloud authentication |

### Running

```bash
python app.py
# Open http://localhost:8080
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Web framework | Flask 3.1 |
| PDF extraction | pdfplumber (primary) + LlamaParse (fallback) |
| Text chunking | LangChain RecursiveCharacterTextSplitter |
| Token counting | tiktoken |
| Embeddings | OpenAI text-embedding-3-small (1536 dim) |
| Vector database | Qdrant (local or cloud) |
| AI generation | Anthropic Claude 3 Haiku |
| Production server | Gunicorn |
