"""
PDF to Markdown Converter using Marker
Converts PDF documents to high-quality Markdown format
"""

import os
import sys
from pathlib import Path
from marker.convert import convert_single_pdf
from marker.models import load_all_models


def convert_pdf_to_markdown(pdf_path: str, output_dir: str = None) -> dict:
    """
    Convert a PDF file to Markdown format using Marker.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the markdown file (optional)

    Returns:
        Dictionary with conversion results including:
        - markdown: The converted markdown text
        - metadata: PDF metadata
        - output_path: Path where markdown was saved
    """
    # Validate input
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Setup output directory
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path) or "."
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename
    pdf_name = Path(pdf_path).stem
    output_path = os.path.join(output_dir, f"{pdf_name}.md")

    print(f"Loading Marker models...")
    # Load the AI models (only loaded once, cached afterwards)
    model_lst = load_all_models()

    print(f"Converting PDF: {pdf_path}")
    # Convert PDF to markdown
    full_text, images, out_meta = convert_single_pdf(
        pdf_path,
        model_lst
    )

    # Save markdown to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"✓ Markdown saved to: {output_path}")
    print(f"✓ Pages processed: {out_meta.get('pages', 'N/A')}")

    return {
        "markdown": full_text,
        "metadata": out_meta,
        "output_path": output_path,
        "images": images
    }


def batch_convert_pdfs(pdf_dir: str, output_dir: str = None):
    """
    Convert all PDF files in a directory to Markdown.

    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory to save markdown files
    """
    if output_dir is None:
        output_dir = os.path.join(pdf_dir, "markdown_output")

    os.makedirs(output_dir, exist_ok=True)

    # Find all PDF files
    pdf_files = list(Path(pdf_dir).glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return

    print(f"Found {len(pdf_files)} PDF file(s)")

    # Load models once for batch processing
    print("Loading Marker models...")
    model_lst = load_all_models()

    # Convert each PDF
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Converting: {pdf_path.name}")
        try:
            output_path = os.path.join(output_dir, f"{pdf_path.stem}.md")
            full_text, images, out_meta = convert_single_pdf(
                str(pdf_path),
                model_lst
            )

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)

            print(f"  ✓ Saved to: {output_path}")
            print(f"  ✓ Pages: {out_meta.get('pages', 'N/A')}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print(f"\n✓ Batch conversion complete! Files saved in: {output_dir}")


def main():
    """Command-line interface for PDF to Markdown conversion."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert PDF documents to Markdown using Marker"
    )
    parser.add_argument(
        "input",
        help="Path to PDF file or directory containing PDFs"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory for markdown files",
        default=None
    )
    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        help="Batch mode: convert all PDFs in input directory"
    )

    args = parser.parse_args()

    try:
        if args.batch:
            batch_convert_pdfs(args.input, args.output)
        else:
            convert_pdf_to_markdown(args.input, args.output)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
