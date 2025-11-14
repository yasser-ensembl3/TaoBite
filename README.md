# Tao of Founders - Knowledge Base

A powerful PDF processing and knowledge extraction system that converts PDFs to Markdown, creates vector embeddings, and extracts meaningful quotes using AI.

## Features

- 📄 **PDF to Markdown Conversion** - Ultra-fast conversion using LlamaParse cloud API
- 🔪 **Intelligent Chunking** - Smart text splitting with configurable token sizes
- 🧠 **Vector Embeddings** - OpenAI embeddings for semantic search
- 🔍 **Semantic Search** - Qdrant vector database for similarity matching (Cloud & Local)
- 📚 **Quote Extraction** - AI-powered citation extraction with Claude
- 🎯 **Relevance Scoring** - See how relevant each quote is to your search
- ☁️ **Qdrant Cloud Integration** - Deploy vector database to cloud for production use

## Setup

### 1. Clone the repository

```bash
git clone git@github.com:yasser-ensembl3/TaoBite.git
cd TaoBite
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
LLAMA_CLOUD_API_KEY=your_llamaparse_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Qdrant Cloud (leave empty to use local storage)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

**Get API keys:**
- LlamaParse: https://cloud.llamaindex.ai/
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Qdrant Cloud: https://cloud.qdrant.io/

### 5. Run the application

```bash
python app.py
```

The application will be available at: http://localhost:8080

## Usage

### 1. Upload and Process PDFs

1. Go to http://localhost:8080
2. Upload a PDF file
3. Click "Convert to Markdown"
4. Use "Auto Pipeline" to automatically chunk, embed, and inject into vector database

### 2. Extract Quotes

1. Once documents are in the knowledge base, go to "Quote Extractor"
2. Enter keywords or topics (e.g., "flow state", "entrepreneurship")
3. Get relevant quotes with author attribution and relevance scores
4. Download as Markdown for your Substack notes

### 3. Migrate to Qdrant Cloud

To deploy your vector database to the cloud:

```bash
python migrate_to_qdrant_cloud.py
```

This will transfer all vectors from local storage to your Qdrant Cloud cluster.

## Tech Stack

- **Backend**: Flask (Python)
- **PDF Parsing**: LlamaParse
- **Embeddings**: OpenAI (text-embedding-3-small)
- **Vector DB**: Qdrant (Cloud & Local)
- **AI**: Claude 3 Haiku (Anthropic)
- **Text Processing**: LangChain, tiktoken

## Security

⚠️ **IMPORTANT**: Never commit your `.env` file to Git. It contains sensitive API keys.

The `.gitignore` file is configured to exclude:
- `.env` files
- `uploads/` folder
- `outputs/` folder
- `qdrant_storage/` database

## Project Structure

```
TaoBite/
├── app.py                        # Main Flask application
├── migrate_to_qdrant_cloud.py   # Cloud migration script
├── test_qdrant_cloud.py         # Cloud connection test
├── templates/                    # HTML templates
│   ├── index.html               # Main upload interface
│   └── quote_extractor.html     # Quote extraction interface
├── uploads/                     # Uploaded PDFs (gitignored)
├── outputs/                     # Converted Markdown files (gitignored)
├── qdrant_storage/              # Local vector database (gitignored)
├── .env                         # API keys (gitignored)
├── .env.example                 # Example environment file
└── requirements.txt             # Python dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
