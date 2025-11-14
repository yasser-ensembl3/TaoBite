"""
Obsidian PDF to Markdown Converter
Converts PDFs to Markdown with smart tracking, auto-categorization, and auto-tagging
Uses pdfplumber first, falls back to LlamaParse if extraction fails
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pdfplumber
from pypdf import PdfReader
import re

# Optional LlamaParse import
try:
    from llama_parse import LlamaParse
    LLAMAPARSE_AVAILABLE = True
except ImportError:
    LLAMAPARSE_AVAILABLE = False
    print("⚠️  LlamaParse not available. Install with: pip install llama-parse")


class ObsidianPDFConverter:
    """
    Smart PDF to Markdown converter for Obsidian vaults.

    Features:
    - MD5 hash tracking to avoid reprocessing
    - Auto-categorization based on folder structure
    - Auto-tagging from folder names and content
    - YAML frontmatter generation
    - Page-by-page extraction with pdfplumber
    """

    def __init__(self, vault_root: str = "~/Obsidian", llamaparse_api_key: Optional[str] = None):
        """
        Initialize the converter.

        Args:
            vault_root: Root directory of the Obsidian vault
            llamaparse_api_key: API key for LlamaParse (optional, for fallback)
        """
        self.vault_root = Path(vault_root).expanduser().resolve()
        self.tracking_file = self.vault_root / ".pdf_conversion_tracking.json"
        self.skip_dirs = {".obsidian", "node_modules", ".git", "__pycache__"}

        # Initialize LlamaParse if available and API key provided
        self.llamaparse_parser = None
        if LLAMAPARSE_AVAILABLE and llamaparse_api_key:
            try:
                self.llamaparse_parser = LlamaParse(
                    api_key=llamaparse_api_key,
                    result_type="markdown",
                    verbose=False,
                    language="en"
                )
                print("✓ LlamaParse fallback enabled")
            except Exception as e:
                print(f"⚠️  Could not initialize LlamaParse: {e}")

        # Category mappings (folder patterns -> category)
        self.category_patterns = {
            "knowledge/business breakdowns": "business-analysis",
            "knowledge/founders": "biography",
            "knowledge/invest like the best": "investment-research",
            "books": "books",
            "admin": "admin-legal",
            "legal": "admin-legal",
            "code": "code-documentation"
        }

        # Notable figures for auto-tagging
        self.notable_figures = {
            "buffett", "warren buffett", "bezos", "jeff bezos",
            "musk", "elon musk", "jobs", "steve jobs", "gates", "bill gates",
            "graham", "paul graham", "thiel", "peter thiel", "zuckerberg"
        }

        # Load or initialize tracking data
        self.tracking_data = self._load_tracking_data()

    def _load_tracking_data(self) -> Dict:
        """Load the tracking JSON file."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️  Corrupted tracking file, creating new one")
                return {"processed": {}, "failed": {}}
        return {"processed": {}, "failed": {}}

    def _save_tracking_data(self):
        """Save the tracking data to JSON."""
        self.vault_root.mkdir(parents=True, exist_ok=True)
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.tracking_data, indent=2, fp=f)

    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _should_process(self, pdf_path: Path) -> Tuple[bool, str]:
        """
        Check if PDF should be processed.

        Returns:
            (should_process, reason)
        """
        pdf_str = str(pdf_path.relative_to(self.vault_root))
        current_hash = self._calculate_md5(pdf_path)

        # Check if already processed successfully
        if pdf_str in self.tracking_data["processed"]:
            stored_hash = self.tracking_data["processed"][pdf_str].get("hash")
            if stored_hash == current_hash:
                return False, "Already processed (hash match)"
            else:
                return True, "File modified (hash changed)"

        # Check if previously failed
        if pdf_str in self.tracking_data["failed"]:
            return True, "Retry failed conversion"

        return True, "New file"

    def _extract_text_with_pdfplumber(self, pdf_path: Path) -> Tuple[str, Dict, str]:
        """
        Extract text from PDF using pdfplumber.

        Returns:
            (markdown_text, metadata, method_used)
        """
        markdown_lines = []

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text from page
                text = page.extract_text()

                if text:
                    # Add page marker
                    markdown_lines.append(f"---\n### Page {page_num} of {total_pages}\n")
                    markdown_lines.append(text)
                    markdown_lines.append("\n")

        full_text = "\n".join(markdown_lines)

        # Quality gate: minimum 100 characters
        if len(full_text.strip()) < 100:
            raise ValueError(f"Extracted text too short ({len(full_text)} chars). Likely extraction failure.")

        # Extract metadata using pypdf
        try:
            reader = PdfReader(pdf_path)
            metadata = {
                "pages": len(reader.pages),
                "title": reader.metadata.title if reader.metadata else None,
                "author": reader.metadata.author if reader.metadata else None,
                "subject": reader.metadata.subject if reader.metadata else None,
            }
        except Exception as e:
            print(f"⚠️  Could not extract metadata: {e}")
            metadata = {"pages": total_pages}

        return full_text, metadata, "pdfplumber"

    def _extract_text_with_llamaparse(self, pdf_path: Path) -> Tuple[str, Dict, str]:
        """
        Extract text from PDF using LlamaParse (fallback method).

        Returns:
            (markdown_text, metadata, method_used)
        """
        if not self.llamaparse_parser:
            raise ValueError("LlamaParse not available or not initialized")

        print("  🔄 Trying LlamaParse fallback...")

        # Convert with LlamaParse
        documents = self.llamaparse_parser.load_data(str(pdf_path))

        # Extract markdown
        full_text = "\n\n".join([doc.text for doc in documents])

        # Quality gate
        if len(full_text.strip()) < 100:
            raise ValueError(f"LlamaParse extraction too short ({len(full_text)} chars)")

        # Extract metadata using pypdf
        try:
            reader = PdfReader(pdf_path)
            metadata = {
                "pages": len(reader.pages),
                "title": reader.metadata.title if reader.metadata else None,
                "author": reader.metadata.author if reader.metadata else None,
                "subject": reader.metadata.subject if reader.metadata else None,
            }
        except Exception as e:
            print(f"⚠️  Could not extract metadata: {e}")
            metadata = {"pages": len(documents)}

        return full_text, metadata, "llamaparse"

    def _categorize_from_path(self, pdf_path: Path) -> str:
        """
        Auto-categorize based on folder path.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Category string
        """
        relative_path = pdf_path.relative_to(self.vault_root)
        path_lower = str(relative_path.parent).lower()

        for pattern, category in self.category_patterns.items():
            if pattern in path_lower:
                return category

        return "general"

    def _generate_tags(self, pdf_path: Path, text_content: str, category: str) -> List[str]:
        """
        Generate tags from folder path and content.

        Args:
            pdf_path: Path to PDF
            text_content: Extracted text content
            category: Document category

        Returns:
            List of tags
        """
        tags = set()

        # Tags from folder path
        relative_path = pdf_path.relative_to(self.vault_root)
        for part in relative_path.parent.parts:
            # Clean and normalize folder name
            tag = part.lower().replace(" ", "-").replace("_", "-")
            # Skip common/generic folder names
            if tag and tag not in {"knowledge", "documents", "files"}:
                tags.add(tag)

        # Add category tag if not "general"
        if category != "general":
            tags.add(category)

        # Detect notable figures in content
        text_lower = text_content.lower()
        for figure in self.notable_figures:
            if figure in text_lower:
                tags.add("notable-figure")
                break

        return sorted(list(tags))

    def _generate_frontmatter(
        self,
        pdf_path: Path,
        metadata: Dict,
        category: str,
        tags: List[str],
        conversion_date: str
    ) -> str:
        """
        Generate YAML frontmatter for the markdown file.

        Args:
            pdf_path: Original PDF path
            metadata: PDF metadata
            category: Document category
            tags: List of tags
            conversion_date: ISO format date

        Returns:
            YAML frontmatter string
        """
        frontmatter_lines = ["---"]

        # Title (from metadata or filename)
        title = metadata.get("title") or pdf_path.stem
        frontmatter_lines.append(f'title: "{title}"')

        # Author
        if metadata.get("author"):
            frontmatter_lines.append(f'author: "{metadata["author"]}"')

        # Category
        frontmatter_lines.append(f'category: {category}')

        # Tags
        if tags:
            frontmatter_lines.append(f'tags: [{", ".join(tags)}]')
        else:
            frontmatter_lines.append('tags: []')

        # Source
        frontmatter_lines.append(f'source: pdf')
        frontmatter_lines.append(f'pdf_path: "{str(pdf_path.relative_to(self.vault_root))}"')

        # Dates
        frontmatter_lines.append(f'converted_date: {conversion_date}')

        # Page count
        if metadata.get("pages"):
            frontmatter_lines.append(f'pages: {metadata["pages"]}')

        frontmatter_lines.append("---\n")

        return "\n".join(frontmatter_lines)

    def convert_pdf(self, pdf_path: Path, force: bool = False) -> bool:
        """
        Convert a single PDF to Markdown.

        Args:
            pdf_path: Path to PDF file
            force: Force conversion even if already processed

        Returns:
            True if successful, False otherwise
        """
        pdf_path = Path(pdf_path).resolve()

        # Check if in vault
        if not str(pdf_path).startswith(str(self.vault_root)):
            print(f"⚠️  PDF not in vault: {pdf_path}")
            return False

        # Check if should process
        if not force:
            should_process, reason = self._should_process(pdf_path)
            if not should_process:
                print(f"⏭️  Skipping {pdf_path.name}: {reason}")
                return False
            else:
                print(f"📄 Processing {pdf_path.name}: {reason}")

        try:
            # Try pdfplumber first
            print(f"  📖 Extracting text with pdfplumber...")
            method_used = None

            try:
                text_content, metadata, method_used = self._extract_text_with_pdfplumber(pdf_path)
                print(f"  ✓ Extraction successful with pdfplumber")
            except Exception as pdfplumber_error:
                print(f"  ⚠️  pdfplumber failed: {str(pdfplumber_error)}")

                # Try LlamaParse fallback if available
                if self.llamaparse_parser:
                    try:
                        text_content, metadata, method_used = self._extract_text_with_llamaparse(pdf_path)
                        print(f"  ✓ Extraction successful with LlamaParse")
                    except Exception as llamaparse_error:
                        print(f"  ❌ LlamaParse also failed: {str(llamaparse_error)}")
                        raise ValueError(f"Both methods failed. pdfplumber: {str(pdfplumber_error)}, LlamaParse: {str(llamaparse_error)}")
                else:
                    # No fallback available
                    raise pdfplumber_error

            # Categorize
            category = self._categorize_from_path(pdf_path)
            print(f"  📂 Category: {category}")

            # Generate tags
            tags = self._generate_tags(pdf_path, text_content, category)
            print(f"  🏷️  Tags: {tags}")

            # Generate frontmatter
            conversion_date = datetime.now().isoformat()
            frontmatter = self._generate_frontmatter(
                pdf_path, metadata, category, tags, conversion_date
            )

            # Create markdown file (same location as PDF, .md extension)
            md_path = pdf_path.with_suffix('.md')

            # Write markdown
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
                f.write("\n")
                f.write(text_content)

            print(f"  ✅ Saved to: {md_path.name} (method: {method_used})")

            # Update tracking data
            pdf_str = str(pdf_path.relative_to(self.vault_root))
            self.tracking_data["processed"][pdf_str] = {
                "hash": self._calculate_md5(pdf_path),
                "converted_date": conversion_date,
                "md_path": str(md_path.relative_to(self.vault_root)),
                "category": category,
                "tags": tags,
                "method": method_used  # Track which method was used
            }

            # Remove from failed if present
            if pdf_str in self.tracking_data["failed"]:
                del self.tracking_data["failed"][pdf_str]

            self._save_tracking_data()

            return True

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

            # Track failure
            pdf_str = str(pdf_path.relative_to(self.vault_root))
            self.tracking_data["failed"][pdf_str] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._save_tracking_data()

            return False

    def scan_vault(self, force: bool = False) -> Dict[str, int]:
        """
        Scan entire vault for PDFs and convert them.

        Args:
            force: Force conversion of all PDFs

        Returns:
            Statistics dictionary
        """
        stats = {
            "total": 0,
            "processed": 0,
            "skipped": 0,
            "failed": 0
        }

        print(f"\n🔍 Scanning vault: {self.vault_root}")
        print(f"📋 Skip directories: {self.skip_dirs}\n")

        # Find all PDFs
        for pdf_path in self.vault_root.rglob("*.pdf"):
            # Skip if in excluded directory
            if any(skip_dir in pdf_path.parts for skip_dir in self.skip_dirs):
                continue

            stats["total"] += 1

            success = self.convert_pdf(pdf_path, force=force)

            if success:
                stats["processed"] += 1
            elif not force:
                stats["skipped"] += 1
            else:
                stats["failed"] += 1

        return stats

    def print_stats(self):
        """Print tracking statistics."""
        print("\n📊 Conversion Statistics")
        print("=" * 50)
        print(f"✅ Successfully processed: {len(self.tracking_data['processed'])}")
        print(f"❌ Failed conversions: {len(self.tracking_data['failed'])}")

        if self.tracking_data['failed']:
            print("\n❌ Failed Files:")
            for pdf_path, info in self.tracking_data['failed'].items():
                print(f"  • {pdf_path}")
                print(f"    Error: {info['error']}")
                print(f"    Time: {info['timestamp']}")


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert PDFs to Markdown for Obsidian vaults"
    )
    parser.add_argument(
        "--vault",
        default="~/Obsidian",
        help="Path to Obsidian vault (default: ~/Obsidian)"
    )
    parser.add_argument(
        "--file",
        help="Convert a single PDF file"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force conversion even if already processed"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print conversion statistics"
    )

    args = parser.parse_args()

    # Initialize converter
    converter = ObsidianPDFConverter(vault_root=args.vault)

    if args.stats:
        converter.print_stats()
        return

    if args.file:
        # Convert single file
        pdf_path = Path(args.file).resolve()
        converter.convert_pdf(pdf_path, force=args.force)
    else:
        # Scan entire vault
        stats = converter.scan_vault(force=args.force)

        print("\n" + "=" * 50)
        print("📊 Scan Complete")
        print("=" * 50)
        print(f"Total PDFs found: {stats['total']}")
        print(f"✅ Processed: {stats['processed']}")
        print(f"⏭️  Skipped: {stats['skipped']}")
        print(f"❌ Failed: {stats['failed']}")

        converter.print_stats()


if __name__ == "__main__":
    main()
