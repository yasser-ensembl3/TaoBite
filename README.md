# Tao of Founders - AI Knowledge Base System

A powerful PDF-based knowledge management system with flexible AI content generation. Upload PDFs, build vector embeddings, and generate custom content (quotes, posts, summaries, insights) using Claude AI with strict anti-hallucination controls.

## 🚀 Key Features

### AI Content Generation
- 🤖 **Flexible Content Generator** - Custom instructions for ANY output type (quotes, LinkedIn posts, summaries, key terms, insights)
- 📋 **Quick Templates** - One-click presets for common use cases
- 🎯 **Context Control** - Adjustable passage count (5-20) for generation
- 🔒 **Anti-Hallucination** - Strict word-for-word extraction, no paraphrasing
- 📊 **Source Verification** - Full source chunks returned for transparency

### Knowledge Base
- 📄 **Dual PDF Extraction** - pdfplumber (free, local) with LlamaParse fallback
- 🔪 **Smart Chunking** - Intelligent text splitting with token-aware overlap
- 🧠 **Vector Embeddings** - OpenAI embeddings for semantic search
- ☁️ **Qdrant Cloud** - Production-ready vector database (local fallback available)
- 📚 **Database Overview** - Browse all stored documents with stats

### User Experience
- 🎨 **Clean Interface** - Single-page app with collapsible sections
- 📖 **Quick Start Guide** - Built-in instructions for new users
- 🔐 **Separate Admin** - Dedicated page for document uploads
- 📥 **Export** - Download generated content as Markdown

## 📋 Setup

### 1. Clone and Install

```bash
git clone git@github.com:yasser-ensembl3/TaoBite.git
cd TaoBite
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional (for LlamaParse fallback)
LLAMA_CLOUD_API_KEY=your_llamaparse_api_key_here

# Optional (for Qdrant Cloud deployment)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

**Get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- LlamaParse (optional): https://cloud.llamaindex.ai/
- Qdrant Cloud (optional): https://cloud.qdrant.io/

### 3. Run the Application

```bash
python app.py
```

Access at: **http://localhost:8080**

## 🎯 Usage Guide

### Step 1: Generate Content from Knowledge Base

1. **Enter Keywords** - Topics for semantic search (e.g., "resilience", "decision-making")
2. **Choose Template** (optional) - Quick presets: Quotes, Post, Summary, Keywords, Insights
3. **Or Write Custom Instructions** - Tell Claude exactly what you want
4. **Adjust Context Size** - Select 5-20 relevant passages
5. **Generate** - Get AI-generated content based on your instructions

**Example Instructions:**
```
Extract the 5 best quotes about leadership
Write a 200-word LinkedIn post about grit and perseverance
Summarize the key concepts of decision-making under uncertainty
List 10 important terms about entrepreneurship with definitions
```

### Step 2: Add Documents (Admin)

1. Click **"Admin Access"** button
2. Upload PDF files (drag & drop or click)
3. System automatically:
   - Extracts text (pdfplumber → LlamaParse fallback)
   - Chunks content intelligently
   - Generates embeddings (OpenAI)
   - Injects into vector database (Qdrant)

### Step 3: Browse Database

1. Expand **"Database Overview"** section
2. View all stored documents with:
   - Chunk counts
   - Token statistics
   - Source information
   - Preview of chunks

## 🔒 Anti-Hallucination Features

The system prevents AI fabrication through:

1. **Relevance Filtering** - Minimum score threshold (default 30%)
2. **Source Verification** - Full source chunks returned with every response
3. **Strict Extraction Rules**:
   - Word-for-word copying (no paraphrasing)
   - No section titles or headers
   - No survey/questionnaire items
   - Substantive quotes only (15+ words)
   - Quality over quantity

4. **Smart Refusal** - Claude refuses if content doesn't meet quality standards
5. **Transparent Scoring** - Relevance scores shown for each source

## 🏗️ Tech Stack

- **Backend**: Flask (Python)
- **PDF Extraction**: pdfplumber (primary) + LlamaParse (fallback)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Vector Database**: Qdrant Cloud / Local
- **AI Generation**: Claude 3 Haiku (Anthropic)
- **Text Processing**: LangChain, tiktoken

## 📁 Project Structure

```
TaoBite/
├── app.py                           # Main Flask application
├── migrate_to_qdrant_cloud.py      # Cloud migration script
├── obsidian_pdf_converter.py       # PDF converter utility
├── templates/
│   ├── index.html                  # Main interface (AI Generator + DB Overview)
│   ├── admin.html                  # Admin upload page
│   ├── database_overview.html      # Standalone DB viewer
│   ├── draft_generator.html        # Substack draft generator
│   └── quote_extractor.html        # Legacy quote extractor
├── uploads/                        # Uploaded PDFs (gitignored)
├── outputs/                        # Converted Markdown (gitignored)
├── qdrant_storage/                 # Local vector DB (gitignored)
├── .env                            # API keys (gitignored)
├── .env.example                    # Example environment file
└── requirements.txt                # Python dependencies
```

## 🔄 API Endpoints

### Content Generation
- `POST /generate-content` - Generate custom content with instructions
- `POST /extract-quotes` - Extract quotes (legacy)
- `POST /generate-draft` - Generate Substack drafts

### Document Management
- `POST /upload` - Upload PDF
- `POST /auto-pipeline/<job_id>` - Auto-process (chunk + embed + inject)
- `GET /status/<job_id>` - Check processing status

### Database
- `GET /api/database/stats` - Global database statistics
- `GET /api/database/documents` - List all documents with metadata
- `POST /qdrant/search` - Semantic search

## 🚀 Deployment

### Qdrant Cloud Migration

To deploy your vector database to production:

```bash
python migrate_to_qdrant_cloud.py
```

This transfers all vectors from local storage to Qdrant Cloud.

### Environment Variables (Production)

For platforms like Render or Vercel, set these environment variables:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLAMA_CLOUD_API_KEY=llx-...
QDRANT_URL=https://...qdrant.io
QDRANT_API_KEY=...
PORT=8080  # Optional, defaults to 8080
```

## 🔐 Security

⚠️ **Never commit `.env` to Git!**

The `.gitignore` excludes:
- `.env` files (API keys)
- `uploads/` (user PDFs)
- `outputs/` (converted files)
- `qdrant_storage/` (local database)
- `__pycache__/` and `.pyc` files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **LlamaParse** - High-quality PDF parsing
- **Qdrant** - Lightning-fast vector database
- **OpenAI** - Semantic embeddings
- **Anthropic** - Claude AI for generation
- **pdfplumber** - Free local PDF extraction

---

Built with ❤️ for knowledge workers and founders
