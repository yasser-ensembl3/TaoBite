"""
Test script for Obsidian PDF Converter
"""

from pathlib import Path
from obsidian_pdf_converter import ObsidianPDFConverter

def test_single_file():
    """Test conversion of a single PDF file."""

    # Use uploads folder as test vault
    test_vault = Path(__file__).parent / "uploads"

    # Find a small PDF for testing
    test_pdf = test_vault / "0d54ae18-2096-4fb2-91e4-9328e1e3e538_Flow_The_Psychology_of_Optimal_Experience_1_1.pdf"

    if not test_pdf.exists():
        print(f"❌ Test PDF not found: {test_pdf}")
        # Try to find any PDF
        pdfs = list(test_vault.glob("*.pdf"))
        if pdfs:
            test_pdf = pdfs[0]
            print(f"📄 Using alternative PDF: {test_pdf.name}")
        else:
            print("❌ No PDFs found in uploads folder")
            return

    print("=" * 60)
    print("Testing Obsidian PDF Converter")
    print("=" * 60)
    print(f"Vault: {test_vault}")
    print(f"PDF: {test_pdf.name}")
    print()

    # Initialize converter
    converter = ObsidianPDFConverter(vault_root=str(test_vault))

    # Convert the PDF
    print("🚀 Starting conversion...\n")
    success = converter.convert_pdf(test_pdf, force=True)

    if success:
        print("\n✅ Conversion successful!")

        # Check if markdown was created
        md_path = test_pdf.with_suffix('.md')
        if md_path.exists():
            print(f"\n📄 Markdown file created: {md_path.name}")
            print(f"📊 File size: {md_path.stat().st_size / 1024:.1f} KB")

            # Show first 50 lines
            print("\n📖 Preview (first 50 lines):")
            print("-" * 60)
            with open(md_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:50], 1):
                    print(f"{i:3d}: {line.rstrip()}")

            if len(lines) > 50:
                print(f"\n... ({len(lines) - 50} more lines)")

        # Show tracking data
        print("\n" + "=" * 60)
        print("📋 Tracking Data")
        print("=" * 60)
        converter.print_stats()

    else:
        print("\n❌ Conversion failed!")
        converter.print_stats()

if __name__ == "__main__":
    test_single_file()
