# Tao of Founders - Knowledge Base System

## Overview

A powerful PDF-based knowledge management system with flexible AI content generation. Upload PDFs, build vector embeddings, and generate custom content (quotes, posts, summaries, insights) using Claude AI with strict anti-hallucination controls. Built specifically for curating insights from founder psychology, decision-making, and entrepreneurship literature.

## Core Features

### 1. Flexible AI Content Generator
- **Custom Instructions**: Tell Claude exactly what you want - any output format, any use case
- **Quick Templates**: One-click presets for common needs:
  - Quotes: Extract best quotes with strict word-for-word extraction
  - LinkedIn Post: Generate 200-word professional posts
  - Summary: Create comprehensive overviews
  - Key Terms: Extract and define important concepts
  - Insights: Generate actionable takeaways
- **Context Control**: Adjustable passage count (5-20) for semantic search
- **Anti-Hallucination System**:
  - Relevance filtering with minimum 30% threshold
  - Word-for-word extraction (no paraphrasing)
  - No section titles or questionnaire items
  - Quality over quantity (substantive content only)
  - Full source chunks returned for verification
- **Source Transparency**: Every response includes relevance scores and source passages

### 2. PDF to Markdown Conversion
- **Primary Method**: pdfplumber (local, free, fast)
- **Fallback**: LlamaParse Cloud API (for scanned PDFs or failures)
- **Strategy**: Try pdfplumber first, automatically fall back to LlamaParse if needed
- **Quality Gate**: Minimum 100 characters extracted
- **Speed**: Fast local processing for text-based PDFs
- **OCR**: LlamaParse handles scanned documents
- **Language**: Supports French and other languages
- **Output**: Clean Markdown format with page markers
- **Tracking**: Records which method was used for each conversion

### 3. Intelligent Text Chunking
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

### 4. Vector Embeddings
- **Model**: OpenAI text-embedding-3-small
- **Dimensions**: 1536
- **Batch Processing**: 100 texts per batch (OpenAI limit: 2048)
- **Use Case**: Semantic search and similarity matching

### 5. Vector Database
- **Database**: Qdrant Cloud (with local fallback)
- **Collection**: `pdf_documents` (single unified collection)
- **Distance Metric**: Cosine similarity
- **Deployment**:
  - **Production**: Qdrant Cloud (https://cloud.qdrant.io/)
  - **Development**: Local storage (`./qdrant_storage/`)
  - **Migration Tool**: `migrate_to_qdrant_cloud.py`
- **Features**:
  - Persistent cloud storage (production)
  - Fast similarity search
  - Metadata filtering support
  - Automatic local/cloud detection via environment variables

### 6. Database Overview & Administration
- **Separate Admin Page**: `/admin` for document uploads
- **Database Viewer**: Browse all stored documents with statistics
- **Document Stats**:
  - Chunk counts per document
  - Token statistics
  - Source information
  - Preview of content chunks
- **Real-time Updates**: Auto-refresh after uploads

### 7. Semantic Search
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

### Content Generation & Search

#### `POST /generate-content`
**Primary endpoint** - Generate custom AI content with flexible instructions.
- **Input JSON**:
  ```json
  {
    "keywords": "resilience, decision-making",
    "instructions": "Extract the 5 best quotes about leadership",
    "collection_name": "pdf_documents",
    "top_k": 10
  }
  ```
- **Process**:
  1. Semantic search for relevant chunks (top_k passages)
  2. Filter by relevance threshold (min 30%)
  3. Claude generates content following custom instructions
  4. Returns content with source verification
- **Returns**:
  - Generated content (quotes, posts, summaries, etc.)
  - Source chunks with relevance scores
  - Full transparency for anti-hallucination
- **Anti-Hallucination**:
  - Strict word-for-word extraction rules
  - Quality filters (no headers, no surveys)
  - Substantive content only (15+ words)

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
**Legacy endpoint** - Extract quotes (now superseded by /generate-content).
- Kept for backward compatibility
- Recommend using /generate-content with "Extract quotes" instructions

#### `POST /generate-draft`
**Legacy endpoint** - Generate Substack drafts.
- Kept for backward compatibility
- Recommend using /generate-content with custom instructions

### Utility Endpoints

#### `GET /api/database/stats`
Get global database statistics.
- **Returns**:
  - Total vectors across all collections
  - List of all collections with vector counts
  - Database health metrics

#### `GET /api/database/documents`
List all documents in a collection.
- **Query Parameters**:
  - `collection_name` (default: "pdf_documents")
  - `limit` (default: 100)
- **Returns**:
  - Document metadata (filename, source, chunk count)
  - Token and character statistics
  - Preview of chunks
  - Total counts and summaries

#### `GET /qdrant/collections`
List all Qdrant collections.
- **Returns**: Collection names, vector counts, dimensions

#### `GET /models/status`
Check if services are ready.
- **Returns**: Service availability status

## Web Interface

### Main Page (`/`)
**Template**: `templates/index.html`

**Unified Interface** with three collapsible sections:

1. **AI Content Generator** (default open)
   - Keyword input field
   - Custom instructions textarea
   - Quick template buttons (Quotes, Post, Summary, Keywords, Insights)
   - Context size slider (5-20 passages)
   - Generate button
   - Output display with source chunks and relevance scores
   - Markdown download button
   - Built-in usage guide

2. **Database Overview** (collapsible)
   - Global statistics (total vectors, collections)
   - Document list with metadata
   - Chunk previews per document
   - Token and character counts
   - Real-time stats updates

3. **Admin Access** (button link)
   - Links to `/admin` page
   - Separated to keep main interface clean

**Workflow**:
1. Enter keywords (e.g., "resilience, leadership")
2. Choose template OR write custom instructions
3. Adjust context size (how many passages to use)
4. Click "Generate Content"
5. Review output with source verification
6. Download as Markdown if needed

### Admin Page (`/admin`)
**Template**: `templates/admin.html`

**Dedicated upload interface**:
- Drag & drop PDF upload
- Automatic processing pipeline
- Progress tracking with visual feedback
- Success metrics (chunks, tokens, extraction method)
- Link back to main interface

**Auto-Pipeline Process**:
1. PDF upload
2. Text extraction (pdfplumber → LlamaParse fallback)
3. Automatic chunking
4. Embedding generation
5. Vector database injection
6. Completion summary

### Legacy Pages (Backward Compatibility)

#### Quote Extractor (`/quote-extractor`)
**Template**: `templates/quote_extractor.html`
- Original quote extraction interface
- Kept for users familiar with old workflow
- Recommend migrating to main page AI Content Generator

#### Draft Generator (`/draft-generator`)
**Template**: `templates/draft_generator.html`
- Substack draft generation
- Kept for backward compatibility

#### Database Overview Standalone (`/database-overview`)
**Template**: `templates/database_overview.html`
- Standalone database viewer
- Now integrated into main page

## Configuration Files

### `.env` (Required)
API keys and configuration - **NEVER commit to git**
```
# Required
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional (PDF extraction fallback)
LLAMA_CLOUD_API_KEY=llx-...

# Optional (Qdrant Cloud for production)
QDRANT_URL=https://...qdrant.io
QDRANT_API_KEY=...

# Optional (custom port)
PORT=8080
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

### Why Flexible Instructions over Fixed Endpoints?
- **Versatility**: One endpoint handles any content type (quotes, posts, summaries, insights)
- **User Control**: Users define exactly what they want
- **Future-Proof**: No need to create new endpoints for new content types
- **Template System**: Quick presets for common use cases while maintaining flexibility
- **Reduces Code**: One well-designed endpoint vs. many specialized ones

### Why Anti-Hallucination Focus?
- **Trust**: Users need confidence content comes from actual sources
- **Accuracy**: Word-for-word extraction prevents AI fabrication
- **Verification**: Full source chunks allow users to verify claims
- **Quality**: Relevance threshold filters out weak matches
- **Transparency**: Scores and sources visible for every result

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
- **Cost**: Most economical for high-volume requests
- **Sufficient**: Handles content generation well
- **Following Instructions**: Excellent at adhering to strict extraction rules
- **Quality Output**: Reliable structured responses

### Why Qdrant Cloud with Local Fallback?
- **Production**: Cloud for scalability and reliability
- **Development**: Local for offline work and testing
- **Flexibility**: Automatic detection via environment variables
- **Migration**: Easy transfer with migration script
- **No Vendor Lock**: Can switch back to local anytime

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
├── app.py                           # Main Flask application
├── migrate_to_qdrant_cloud.py      # Cloud migration script
├── obsidian_pdf_converter.py       # PDF converter utility
├── templates/
│   ├── index.html                  # Main interface (AI Generator + DB Overview)
│   ├── admin.html                  # Admin upload page
│   ├── database_overview.html      # Standalone DB viewer (legacy)
│   ├── draft_generator.html        # Substack draft generator (legacy)
│   └── quote_extractor.html        # Legacy quote extractor
├── uploads/                        # Uploaded PDFs (gitignored)
├── outputs/                        # Converted Markdown (gitignored)
├── qdrant_storage/                 # Local vector DB (gitignored)
├── .env                            # API keys (gitignored)
├── .env.example                    # Example environment file
├── .gitignore                      # Git exclusions
├── requirements.txt                # Python dependencies
├── README.md                       # User documentation
└── project.md                      # This file (technical docs)
```

### Key Functions in app.py

**Core Pipeline**:
- `convert_pdf_async()`: Background PDF conversion with pdfplumber/LlamaParse
- `chunk_markdown()`: Intelligent text splitting with token counting
- `get_openai_embeddings()`: Batch embedding generation
- `inject_to_qdrant()`: Store vectors in database with metadata
- `search_qdrant()`: Semantic similarity search

**AI Content Generation**:
- `generate_content()`: New flexible content generator (main endpoint)
- `extract_quotes()`: Legacy quote extraction (backward compatibility)
- `generate_draft()`: Legacy draft generator

**Database Management**:
- `get_database_stats()`: Global statistics
- `get_database_documents()`: List documents with metadata
- `init_qdrant()`: Initialize Qdrant client (cloud or local)

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
