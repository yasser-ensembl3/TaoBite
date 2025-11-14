# Tao of Founders - Knowledge Base System

## Overview

A comprehensive PDF processing and knowledge extraction system that converts PDFs to Markdown, creates vector embeddings, and extracts meaningful quotes using AI. Built specifically for curating insights from founder psychology, decision-making, and entrepreneurship literature.

## Core Features

### 1. PDF to Markdown Conversion
- **Primary Method**: pdfplumber (local, free, fast)
- **Fallback**: LlamaParse Cloud API (for scanned PDFs or failures)
- **Strategy**: Try pdfplumber first, automatically fall back to LlamaParse if needed
- **Quality Gate**: Minimum 100 characters extracted
- **Speed**: Fast local processing for text-based PDFs
- **OCR**: LlamaParse handles scanned documents
- **Language**: Supports French and other languages
- **Output**: Clean Markdown format with page markers
- **Tracking**: Records which method was used for each conversion

### 2. Intelligent Text Chunking
- **Library**: LangChain RecursiveCharacterTextSplitter
- **Token Counting**: tiktoken (cl100k_base encoding)
- **Default Settings**:
  - Chunk size: 1000 tokens
  - Overlap: 200 tokens (maintains context between chunks)
- **Separators**: Prioritizes paragraphs → lines → spaces
- **Metadata**: Each chunk includes:
  - chunk_id
  - content
  - token_count
  - char_count
  - preview (first 100 chars)

### 3. Vector Embeddings
- **Model**: OpenAI text-embedding-3-small
- **Dimensions**: 1536
- **Batch Processing**: 100 texts per batch (OpenAI limit: 2048)
- **Use Case**: Semantic search and similarity matching

### 4. Vector Database
- **Database**: Qdrant (local storage)
- **Collection**: `pdf_documents` (single unified collection)
- **Distance Metric**: Cosine similarity
- **Storage Path**: `./qdrant_storage/`
- **Features**:
  - Persistent local storage
  - Fast similarity search
  - Metadata filtering support

### 5. Quote Extraction with AI
- **Model**: Claude 3 Haiku (Anthropic)
- **Format**: JSON-structured responses
- **Output**:
  - Exact quotes (1-3 sentences)
  - Author attribution or source filename
  - Relevance percentage scores
  - Markdown download format
- **No Translation**: Returns quotes in original language
- **No Reformulation**: Extracts pure citations

### 6. Semantic Search
- **Process**:
  1. User query → OpenAI embedding
  2. Qdrant searches for top-k similar vectors
  3. Returns most relevant chunks with scores
- **Configurable**: Adjustable number of results (top_k)

## Tech Stack

### Backend
- **Framework**: Flask (Python web framework)
- **Server**: Development server (0.0.0.0:8080)
- **Threading**: Async PDF processing

### AI & ML Services
- **pdfplumber**: Primary PDF text extraction (local, free)
- **LlamaParse**: Fallback PDF parsing (cloud API, OCR)
- **OpenAI**:
  - API: Embeddings generation
  - Model: text-embedding-3-small
- **Anthropic**:
  - API: Quote extraction
  - Model: claude-3-haiku-20240307

### Database & Storage
- **Qdrant**: Vector database (local)
- **File System**:
  - uploads/ (PDFs)
  - outputs/ (Markdown files)
  - qdrant_storage/ (vector DB)

### Text Processing
- **LangChain**: Text splitting
- **tiktoken**: Token counting
- **OpenAI Client**: Embedding API calls
- **Anthropic Client**: Claude API calls

### Environment & Security
- **python-dotenv**: Environment variable management
- **API Keys**: Stored in .env (gitignored)
- **File Security**: Secure filename handling (werkzeug)

## API Endpoints

### Core PDF Processing

#### `POST /upload`
Upload a PDF file for conversion.
- **Input**: Multipart form with PDF file
- **Returns**: job_id for tracking
- **Process**: Queues async conversion

#### `GET /status/<job_id>`
Check conversion status.
- **Returns**: Current status (queued, processing, completed, error)

#### `GET /download/<job_id>`
Download converted Markdown file.
- **Requires**: Completed conversion

#### `POST /chunk/<job_id>`
Chunk a converted document.
- **Input JSON**:
  ```json
  {
    "chunk_size": 1000,
    "chunk_overlap": 200
  }
  ```
- **Returns**: Chunks with metadata

#### `POST /inject/<job_id>`
Embed chunks and inject into Qdrant.
- **Input JSON**:
  ```json
  {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "collection_name": "pdf_documents"
  }
  ```
- **Process**:
  1. Chunks document
  2. Generates OpenAI embeddings
  3. Stores in Qdrant with metadata

#### `POST /auto-pipeline/<job_id>`
One-click: Chunk + Embed + Inject.
- **Input JSON**: Same as /inject
- **Returns**: Complete statistics

### Search & Extraction

#### `POST /qdrant/search`
Semantic search in vector database.
- **Input JSON**:
  ```json
  {
    "query": "flow state",
    "collection_name": "pdf_documents",
    "limit": 5
  }
  ```
- **Returns**: Top matching chunks with scores

#### `POST /extract-quotes`
Extract relevant quotes from knowledge base.
- **Input JSON**:
  ```json
  {
    "keywords": "decision-making, psychology",
    "collection_name": "pdf_documents",
    "top_k": 10
  }
  ```
- **Process**:
  1. Semantic search for relevant chunks
  2. Claude extracts 3-5 best quotes
  3. Formats with author and relevance %
- **Returns**: Markdown-formatted quotes

#### `POST /generate-draft`
Generate Substack draft notes (legacy feature).
- **Input JSON**: Same as /extract-quotes
- **Returns**: Longer formatted draft with commentary

### Utility Endpoints

#### `GET /qdrant/collections`
List all Qdrant collections.
- **Returns**: Collection names, vector counts, dimensions

#### `GET /models/status`
Check if services are ready.
- **Returns**: Service availability status

## Web Interface

### Main Page (`/`)
**Template**: `templates/index.html`

**Features**:
- PDF upload form
- Conversion progress tracking
- Download converted Markdown
- "Auto Pipeline" button (one-click embedding)

**Workflow**:
1. Upload PDF
2. Click "Convert to Markdown"
3. Wait for completion
4. Download Markdown OR
5. Click "Auto Pipeline" to embed into knowledge base

### Quote Extractor (`/quote-extractor`)
**Template**: `templates/quote_extractor.html`

**Features**:
- Keyword input
- Number of quotes selector (3-10)
- Real-time quote extraction
- Markdown download button
- Relevance scores display

**Output Format**:
```markdown
# keyword

> "Exact quote from source"
— Author Name (24.3% relevance)

> "Another relevant quote"
— Source Document (23.7% relevance)
```

## Configuration Files

### `.env` (Required)
API keys - **NEVER commit to git**
```
LLAMA_CLOUD_API_KEY=llx-...
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### `.env.example` (Template)
Shows structure without exposing keys.

### `.gitignore`
Excludes:
- `.env` (API keys)
- `uploads/` (uploaded PDFs)
- `outputs/` (converted Markdown)
- `qdrant_storage/` (vector database)
- `venv/` (Python environment)
- `__pycache__/` (Python cache)

## Data Flow

### Upload → Embedding Pipeline

```
PDF Upload
  ↓
Try pdfplumber (local extraction)
  ↓ (if fails)
Fallback to LlamaParse Cloud API
  ↓
Markdown File (saved to outputs/)
  ↓
RecursiveCharacterTextSplitter (chunking)
  ↓
Chunks (1000 tokens each, 200 overlap)
  ↓
OpenAI Embeddings API (vectorization)
  ↓
Qdrant Database (storage)
  ↓
Collection: pdf_documents
```

### Search → Quote Extraction Pipeline

```
User Query (keywords)
  ↓
OpenAI Embeddings API (query vectorization)
  ↓
Qdrant Search (similarity matching)
  ↓
Top-K Most Relevant Chunks
  ↓
Claude 3 Haiku (quote extraction + formatting)
  ↓
Markdown Output (quotes with authors & relevance)
```

## Key Design Decisions

### Why One Collection?
- **Simplified**: All documents in `pdf_documents` collection
- **Consistent**: Single source of truth
- **Efficient**: No confusion between multiple collections
- **Searchable**: All knowledge searchable together

### Why text-embedding-3-small?
- **Cost-effective**: Cheaper than larger models
- **Fast**: Quick embedding generation
- **Sufficient**: 1536 dimensions adequate for semantic search
- **Quality**: High accuracy for citation matching

### Why Claude 3 Haiku?
- **Speed**: Fastest Claude model
- **Cost**: Most economical
- **Sufficient**: Handles quote extraction well
- **JSON**: Reliable structured output

### Why Local Qdrant?
- **Privacy**: Data stays on your machine
- **No Costs**: No cloud database fees
- **Fast**: Local queries = low latency
- **Simple**: No cloud setup required

## Security Considerations

### Protected
✅ API keys in environment variables
✅ `.env` file gitignored
✅ Sensitive folders excluded from git
✅ Secure filename handling

### Not Protected (Development Mode)
⚠️ No authentication on endpoints
⚠️ Development server (not production-ready)
⚠️ Debug mode enabled
⚠️ CORS not configured

### For Production
- Use production WSGI server (gunicorn, uwsgi)
- Add authentication/authorization
- Configure CORS properly
- Disable debug mode
- Use HTTPS
- Add rate limiting

## Usage Statistics

### Tokens per Document
- Average PDF: 10,000 - 50,000 tokens
- Chunks per document: 10-50 chunks (depends on size)
- Average chunk: 1000 tokens

### API Costs (Approximate)
- **pdfplumber**: Free (local processing)
- **LlamaParse**: ~$0.003 per page (only when fallback is needed)
- **OpenAI Embeddings**: ~$0.0001 per 1K tokens
- **Claude Haiku**: ~$0.00025 per 1K input tokens, ~$0.00125 per 1K output tokens

Example for 50-page text-based PDF:
- Parsing (pdfplumber): **$0** (free)
- Embeddings (25K tokens): $0.0025
- Quote extraction (10K input, 500 output): $0.003
- **Total**: ~$0.006 per document

Example for 50-page scanned PDF (LlamaParse fallback):
- Parsing (LlamaParse): $0.15
- Embeddings (25K tokens): $0.0025
- Quote extraction (10K input, 500 output): $0.003
- **Total**: ~$0.16 per document

## Troubleshooting

### Common Issues

**Issue**: "Collection not found"
**Solution**: Upload and embed at least one PDF first

**Issue**: "No quotes returned"
**Solution**: Check collection has vectors, try different keywords

**Issue**: "Module not found"
**Solution**: `pip install -r requirements.txt`

**Issue**: "API key error"
**Solution**: Check `.env` file exists and has valid keys

**Issue**: "Same quotes every time"
**Solution**: Database had old data - now fixed with single collection

## Development

### Project Structure
```
Tao Bite/
├── app.py                      # Main Flask application
├── templates/
│   ├── index.html              # PDF upload & conversion
│   └── quote_extractor.html    # Quote extraction interface
├── uploads/                    # Uploaded PDFs (gitignored)
├── outputs/                    # Converted Markdown (gitignored)
├── qdrant_storage/             # Vector database (gitignored)
├── .env                        # API keys (gitignored)
├── .env.example                # Template
├── .gitignore                  # Git exclusions
├── requirements.txt            # Python dependencies
├── README.md                   # User documentation
└── project.md                  # This file (technical docs)
```

### Key Functions in app.py

- `convert_pdf_async()`: Background PDF conversion
- `chunk_markdown()`: Intelligent text splitting
- `get_openai_embeddings()`: Generate embeddings
- `inject_to_qdrant()`: Store vectors in database
- `extract_quotes()`: AI-powered quote extraction
- `search_qdrant()`: Semantic search

### Adding New Features

**To add a new AI model**:
1. Install client library
2. Add API key to `.env`
3. Initialize client in app.py
4. Create endpoint function
5. Add route decorator

**To add new metadata**:
1. Update `inject_to_qdrant()` payload
2. Modify Qdrant point structure
3. Update search results formatting

## Future Enhancements

### Potential Features
- [ ] Multi-file upload (batch processing)
- [ ] Document categorization/tagging
- [ ] Author entity extraction
- [ ] Citation verification
- [ ] Export to Notion/Roam
- [ ] Web scraping integration
- [ ] Duplicate detection
- [ ] Vector similarity visualization
- [ ] Usage analytics dashboard
- [ ] API rate limiting
- [ ] User authentication
- [ ] Document versioning
- [ ] Full-text search (hybrid with vector search)

### Performance Optimizations
- [ ] Cache frequently accessed embeddings
- [ ] Batch multiple document uploads
- [ ] Async embedding generation
- [ ] Lazy loading for large collections
- [ ] Compression for stored vectors

## References

- [LlamaParse Docs](https://docs.llamaindex.ai/en/stable/api_reference/llama_parse/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Anthropic Claude](https://docs.anthropic.com/claude/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

## License

MIT License

## Support

For issues or questions:
1. Check this documentation
2. Review README.md for setup
3. Check API endpoint logs in console
4. Verify `.env` configuration
