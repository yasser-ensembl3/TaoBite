# Quick Start - Obsidian PDF Converter

## Installation

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies (already done if you have pdfplumber and pypdf)
pip install pdfplumber pypdf
```

## Usage Examples

### 1. Convert Your Entire Obsidian Vault

```bash
# Default vault location (~/Obsidian)
python obsidian_pdf_converter.py

# Custom vault location
python obsidian_pdf_converter.py --vault /path/to/your/vault
```

**What happens:**
- Scans entire vault for PDFs
- Skips `.obsidian`, `node_modules`, `.git`, `__pycache__`
- Converts only new or modified PDFs
- Creates `.md` file next to each PDF
- Saves tracking data to `.pdf_conversion_tracking.json`

### 2. Convert a Single PDF

```bash
python obsidian_pdf_converter.py \
  --vault ~/Obsidian \
  --file ~/Obsidian/Books/flow.pdf
```

**Output:** `~/Obsidian/Books/flow.md`

### 3. Force Reconversion

```bash
# Reconvert everything (ignores tracking)
python obsidian_pdf_converter.py --force

# Reconvert single file
python obsidian_pdf_converter.py --file ~/Obsidian/Books/flow.pdf --force
```

### 4. View Statistics

```bash
python obsidian_pdf_converter.py --stats
```

**Shows:**
- Total files processed
- Failed conversions with reasons
- Timestamps

## Example Output

### Input
`~/Obsidian/Knowledge/Business Breakdowns/amazon.pdf`

### Output File
`~/Obsidian/Knowledge/Business Breakdowns/amazon.md`

### Output Content
```yaml
---
title: "Amazon Business Strategy"
author: "Jeff Bezos"
category: business-analysis
tags: [business-breakdowns, knowledge, notable-figure]
source: pdf
pdf_path: "Knowledge/Business Breakdowns/amazon.pdf"
converted_date: 2025-11-12T10:30:00
pages: 42
---

---
### Page 1 of 42

[Page 1 content here...]

---
### Page 2 of 42

[Page 2 content here...]
```

## Auto-Categorization Examples

| Folder Path | Category |
|------------|----------|
| `Knowledge/Business Breakdowns/` | `business-analysis` |
| `Knowledge/Founders/` | `biography` |
| `Knowledge/Invest Like The Best/` | `investment-research` |
| `Books/` | `books` |
| `Admin/` or `Legal/` | `admin-legal` |
| `Code/` | `code-documentation` |
| Anything else | `general` |

## Auto-Tagging Examples

### From Folder Names
- `Knowledge/Business Breakdowns/` → tags: `[business-breakdowns, knowledge]`
- `Books/Founders/` → tags: `[books, founders]`

### From Content
- Mentions "Buffett", "Bezos", "Musk", "Jobs" → adds `notable-figure` tag

## Programmatic Usage (Python)

```python
from obsidian_pdf_converter import ObsidianPDFConverter
from pathlib import Path

# Initialize
converter = ObsidianPDFConverter(vault_root="~/Obsidian")

# Convert single file
success = converter.convert_pdf(
    Path("~/Obsidian/Books/flow.pdf"),
    force=False  # Skip if already converted
)

# Scan entire vault
stats = converter.scan_vault(force=False)
print(f"Processed: {stats['processed']}")
print(f"Skipped: {stats['skipped']}")
print(f"Failed: {stats['failed']}")

# View statistics
converter.print_stats()
```

## Tracking System

### How It Works

1. **First conversion:** Calculates MD5 hash, saves to tracking file
2. **Subsequent runs:** Checks hash
   - Hash matches → Skip
   - Hash differs → Reconvert (file was modified)
3. **Failed conversions:** Tracked separately, retried on next run

### Tracking File Location
`{vault_root}/.pdf_conversion_tracking.json`

### Reset Tracking
```bash
# Delete tracking file to start fresh
rm ~/Obsidian/.pdf_conversion_tracking.json
```

## Troubleshooting

### Problem: "Extracted text too short"
**Cause:** PDF is image-based (scanned), not text-based

**Solution:**
- Use OCR tool first (Adobe Acrobat, Tesseract)
- Or use LlamaParse API (handles OCR automatically)

### Problem: Wrong category assigned
**Cause:** Folder name doesn't match any pattern

**Solution:**
- Edit `category_patterns` in `obsidian_pdf_converter.py`
- Add your custom folder patterns

### Problem: No tags generated
**Cause:** Generic folder names filtered out

**Solution:**
- Use more specific folder names
- Edit `_generate_tags()` to customize logic

### Problem: Conversion is slow
**Cause:** Large PDFs or many files

**Note:** pdfplumber is local and fast, but large PDFs take time
- LlamaParse (cloud API) is faster for large batches

## Comparison: pdfplumber vs LlamaParse

| Feature | pdfplumber (this tool) | LlamaParse (web app) |
|---------|----------------------|---------------------|
| Cost | Free | Paid API |
| Speed | Fast (local) | Very fast (cloud) |
| Quality | Very good | Excellent |
| OCR | No | Yes |
| Tracking | Yes | No |
| Auto-tagging | Yes | No |
| Obsidian YAML | Yes | No |

**Recommendation:**
- Use pdfplumber for text-based PDFs in Obsidian vault
- Use LlamaParse for scanned documents or highest quality

## Integration with Web App

This project includes both:
1. **Web app** (`app.py`) - Uses LlamaParse for high-quality conversion
2. **Obsidian converter** (`obsidian_pdf_converter.py`) - Uses pdfplumber with smart tracking

Choose based on your needs:
- **Web app:** Quick conversions, RAG pipeline, quote extraction
- **Obsidian converter:** Vault management, automatic tracking, Obsidian integration

## Next Steps

1. Run on your vault: `python obsidian_pdf_converter.py --vault ~/Obsidian`
2. Check the output `.md` files in Obsidian
3. Customize categories and tags in the code
4. Set up a cron job for automatic daily conversion:

```bash
# Example cron job (daily at 2 AM)
0 2 * * * cd /path/to/project && ./venv/bin/python obsidian_pdf_converter.py --vault ~/Obsidian
```

## Support

For issues or questions:
1. Check `OBSIDIAN_CONVERTER_README.md` for detailed documentation
2. Examine failed conversions in tracking file
3. Run with `--stats` to see what failed and why
