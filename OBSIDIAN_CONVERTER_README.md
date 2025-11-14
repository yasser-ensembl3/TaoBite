# Obsidian PDF to Markdown Converter

A smart PDF to Markdown converter designed specifically for Obsidian vaults with intelligent tracking, auto-categorization, and auto-tagging.

## Features

### Smart Tracking System
- **MD5 Hash Tracking**: Avoids reprocessing unchanged PDFs
- **Persistent State**: `.pdf_conversion_tracking.json` at vault root
- **Failure Tracking**: Records failed conversions with reasons and timestamps
- **Modification Detection**: Automatically detects when PDFs are updated

### Text Extraction
- **pdfplumber**: High-quality text extraction (better multi-column handling than PyPDF2)
- **pypdf**: Metadata extraction (title, author, subject, page count)
- **Page Markers**: Inserts "---\n### Page X of Y\n\n" between pages
- **Quality Gate**: Rejects extractions with less than 100 characters

### Auto-Categorization
Maps folder patterns to categories:
- `Knowledge/Business Breakdowns` → `business-analysis`
- `Knowledge/Founders` → `biography`
- `Knowledge/Invest Like The Best` → `investment-research`
- `Books` → `books`
- `Admin` or `Legal` → `admin-legal`
- `Code` → `code-documentation`
- Default → `general`

### Auto-Tagging
Generates tags from:
- **Folder Path**: Converts folder names to tags (lowercase, dash-separated)
- **Category**: Adds category as tag (unless "general")
- **Notable Figures**: Detects mentions of Buffett, Bezos, Musk, Jobs, Gates, Graham, Thiel, Zuckerberg
  - Adds `notable-figure` tag when detected

### YAML Frontmatter
Automatically generates Obsidian-compatible frontmatter:
```yaml
---
title: "Document Title"
author: "Author Name"
category: business-analysis
tags: [business-breakdowns, knowledge, notable-figure]
source: pdf
pdf_path: "Knowledge/Business Breakdowns/example.pdf"
converted_date: 2025-11-12T10:30:00
pages: 42
---
```

## Installation

### Requirements
```bash
pip install pdfplumber pypdf
```

Already installed in this project's virtual environment.

## Usage

### Command Line Interface

#### Scan Entire Vault
```bash
# Default vault location (~/Obsidian)
python obsidian_pdf_converter.py

# Custom vault location
python obsidian_pdf_converter.py --vault /path/to/vault

# Force reprocess all PDFs
python obsidian_pdf_converter.py --force
```

#### Convert Single File
```bash
python obsidian_pdf_converter.py --file ~/Obsidian/path/to/file.pdf

# Force conversion even if already processed
python obsidian_pdf_converter.py --file ~/Obsidian/path/to/file.pdf --force
```

#### View Statistics
```bash
python obsidian_pdf_converter.py --stats
```

### Programmatic Usage

```python
from obsidian_pdf_converter import ObsidianPDFConverter

# Initialize converter
converter = ObsidianPDFConverter(vault_root="~/Obsidian")

# Convert single PDF
converter.convert_pdf(Path("~/Obsidian/Books/example.pdf"))

# Scan entire vault
stats = converter.scan_vault()
print(f"Processed: {stats['processed']}, Failed: {stats['failed']}")

# View statistics
converter.print_stats()
```

## Configuration

### Vault Root
Default: `~/Obsidian`

Change via:
- CLI: `--vault /path/to/vault`
- Code: `ObsidianPDFConverter(vault_root="/path/to/vault")`

### Skip Directories
Automatically skips:
- `.obsidian`
- `node_modules`
- `.git`
- `__pycache__`

### Custom Category Patterns
Edit the `category_patterns` dictionary in `ObsidianPDFConverter.__init__()`:

```python
self.category_patterns = {
    "your/folder/pattern": "your-category",
    # Add more patterns...
}
```

### Custom Notable Figures
Edit the `notable_figures` set in `ObsidianPDFConverter.__init__()`:

```python
self.notable_figures = {
    "your-figure-name",
    # Add more names...
}
```

## Tracking File

Located at: `{vault_root}/.pdf_conversion_tracking.json`

### Structure
```json
{
  "processed": {
    "relative/path/to/file.pdf": {
      "hash": "md5-hash-here",
      "converted_date": "2025-11-12T10:30:00",
      "md_path": "relative/path/to/file.md",
      "category": "business-analysis",
      "tags": ["business-breakdowns", "notable-figure"]
    }
  },
  "failed": {
    "relative/path/to/failed.pdf": {
      "error": "Error message",
      "timestamp": "2025-11-12T10:30:00"
    }
  }
}
```

### Behavior
- **Successful conversion**: Stores hash, prevents reprocessing
- **File modified**: Detects hash change, reconverts
- **Failed conversion**: Records error, allows retry on next run
- **Force mode**: Bypasses all checks, reconverts everything

## Output Format

### Markdown File
- Created in same directory as source PDF
- Same filename with `.md` extension
- Contains YAML frontmatter + extracted text
- Page markers for navigation

### Example Output
```markdown
---
title: "Business Strategy Guide"
author: "John Doe"
category: business-analysis
tags: [business-breakdowns, knowledge, strategy]
source: pdf
pdf_path: "Knowledge/Business Breakdowns/strategy.pdf"
converted_date: 2025-11-12T10:30:00
pages: 25
---

---
### Page 1 of 25

[Extracted text from page 1...]

---
### Page 2 of 25

[Extracted text from page 2...]
```

## Quality Assurance

### Extraction Quality Gate
- Rejects conversions with < 100 characters
- Prevents empty/corrupted extractions
- Logs failures in tracking file

### Error Handling
- Graceful failure with detailed error messages
- Continues processing other files on batch conversion
- Tracks all failures for review

## Comparison with LlamaParse

This converter uses **pdfplumber** instead of LlamaParse:

| Feature | pdfplumber | LlamaParse |
|---------|-----------|------------|
| **Cost** | Free | Paid API |
| **Speed** | Local, fast | Cloud API |
| **Quality** | Very good (multi-column) | Excellent |
| **Metadata** | Via pypdf | Built-in |
| **Tracking** | Built-in | Not included |
| **Auto-tagging** | Built-in | Not included |
| **Obsidian Integration** | Native | Manual |

**Note**: This project still includes LlamaParse as a dependency for the web app (`app.py`). The Obsidian converter (`obsidian_pdf_converter.py`) is a standalone module that doesn't require LlamaParse.

## Troubleshooting

### "Extracted text too short" Error
- PDF may be image-based (scanned document)
- Try OCR tools first (e.g., Adobe Acrobat, Tesseract)
- Or use LlamaParse which handles OCR

### Missing Metadata
- Some PDFs don't have embedded metadata
- Converter uses filename as fallback for title
- Author/subject fields will be omitted

### Wrong Category
- Edit `category_patterns` to match your folder structure
- Use lowercase in patterns for case-insensitive matching
- More specific patterns take precedence

### Tags Not Generated
- Ensure folders have meaningful names
- Check if folder is in skip list
- Generic folder names (e.g., "knowledge") are filtered out

## Integration with Existing App

The web app (`app.py`) continues to use LlamaParse. To integrate the Obsidian converter:

1. Keep both modules separate
2. Add a new route for Obsidian-style conversion
3. Let users choose between LlamaParse (high quality) and pdfplumber (free, tracked)

Example integration:
```python
from obsidian_pdf_converter import ObsidianPDFConverter

@app.route('/convert-obsidian/<job_id>', methods=['POST'])
def convert_obsidian_style(job_id):
    converter = ObsidianPDFConverter(vault_root='./uploads')
    # Convert with Obsidian features...
```

## License

Same as parent project.

## Support

For issues specific to this converter, check:
1. PDF is valid and readable
2. Vault path is correct
3. File permissions are set
4. Tracking file is not corrupted

Delete `.pdf_conversion_tracking.json` to reset all tracking.
