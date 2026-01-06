#!/usr/bin/env python3
"""
PDF Parser for AI Agent Consumption

This utility extracts text content from PDF files and formats it into a
structured Markdown format suitable for AI agent consumption.

Usage:
    python utils/parse_pdf.py <pdf_file> [output_file]
    python utils/parse_pdf.py docs/documents/file.pdf
    python utils/parse_pdf.py docs/documents/file.pdf output.md

Dependencies:
    - pypdf (pip install pypdf)

Output Format:
    - Markdown document with metadata header
    - Page-by-page content with clear separators
    - Character and word counts for context estimation
"""

import argparse
import sys
from pathlib import Path


def extract_pdf_text(pdf_path: Path) -> dict:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with extracted content and metadata
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Error: pypdf library not installed.", file=sys.stderr)
        print("Install with: pip install pypdf", file=sys.stderr)
        sys.exit(1)

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error: Could not read PDF file: {e}", file=sys.stderr)
        sys.exit(1)

    metadata = reader.metadata or {}
    pages = []
    total_chars = 0
    total_words = 0

    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text()
            if text:
                text = text.strip()
                pages.append({"number": page_num, "text": text})
                total_chars += len(text)
                total_words += len(text.split())
        except Exception as e:
            print(f"Warning: Could not extract text from page {page_num}: {e}", file=sys.stderr)
            pages.append({"number": page_num, "text": f"[Error extracting page {page_num}]"})

    return {
        "filename": pdf_path.name,
        "path": str(pdf_path),
        "num_pages": len(reader.pages),
        "metadata": {
            "title": metadata.get("/Title", "N/A"),
            "author": metadata.get("/Author", "N/A"),
            "subject": metadata.get("/Subject", "N/A"),
            "creator": metadata.get("/Creator", "N/A"),
            "producer": metadata.get("/Producer", "N/A"),
            "creation_date": metadata.get("/CreationDate", "N/A"),
        },
        "pages": pages,
        "total_chars": total_chars,
        "total_words": total_words,
        "estimated_tokens": total_words * 1.3,  # Rough estimate for token count
    }


def format_as_markdown(data: dict) -> str:
    """
    Format extracted PDF data as Markdown suitable for AI consumption.

    Args:
        data: Dictionary with extracted PDF content

    Returns:
        Formatted Markdown string
    """
    lines = [
        f"# PDF Content: {data['filename']}",
        "",
        "## Document Metadata",
        "",
        f"- **Source File**: `{data['path']}`",
        f"- **Pages**: {data['num_pages']}",
        f"- **Total Characters**: {data['total_chars']:,}",
        f"- **Total Words**: {data['total_words']:,}",
        f"- **Estimated Tokens**: ~{int(data['estimated_tokens']):,}",
        "",
    ]

    # Add PDF metadata if available
    metadata = data["metadata"]
    if any(v != "N/A" for v in metadata.values()):
        lines.append("### PDF Properties")
        lines.append("")
        for key, value in metadata.items():
            if value and value != "N/A":
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Document Content",
            "",
            "_Note: Content is extracted page-by-page. Formatting, tables, and images are not preserved._",
            "",
        ]
    )

    # Add page content
    for page_data in data["pages"]:
        page_num = page_data["number"]
        text = page_data["text"]

        lines.extend(
            [
                f"### Page {page_num}",
                "",
                text,
                "",
                "---",
                "",
            ]
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract PDF content and format for AI agent consumption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract to stdout
  python utils/parse_pdf.py docs/documents/proposal.pdf

  # Save to file
  python utils/parse_pdf.py docs/documents/proposal.pdf output.md

  # Use in AI agent workflow
  python utils/parse_pdf.py docs/documents/WHDB\\ -\\ Project\\ Description.pdf | head -n 100
        """,
    )
    parser.add_argument("pdf_file", type=Path, help="Path to PDF file to parse")
    parser.add_argument("output_file", type=Path, nargs="?", help="Optional output file (default: stdout)")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Output only metadata summary without full content",
    )

    args = parser.parse_args()

    if not args.pdf_file.exists():
        print(f"Error: File not found: {args.pdf_file}", file=sys.stderr)
        sys.exit(1)

    if args.pdf_file.suffix.lower() != ".pdf":
        print(f"Warning: File does not have .pdf extension: {args.pdf_file}", file=sys.stderr)

    # Extract content
    print(f"Extracting content from: {args.pdf_file}", file=sys.stderr)
    data = extract_pdf_text(args.pdf_file)
    print(
        f"Extracted {data['num_pages']} pages, {data['total_words']:,} words, ~{int(data['estimated_tokens']):,} tokens",
        file=sys.stderr,
    )

    # Generate output
    if args.summary_only:
        output = f"""# PDF Summary: {data['filename']}

- **Pages**: {data['num_pages']}
- **Words**: {data['total_words']:,}
- **Estimated Tokens**: ~{int(data['estimated_tokens']):,}
- **Title**: {data['metadata']['title']}
- **Author**: {data['metadata']['author']}

Use `python utils/parse_pdf.py {data['path']}` to extract full content.
"""
    else:
        output = format_as_markdown(data)

    # Write output
    if args.output_file:
        args.output_file.write_text(output, encoding="utf-8")
        print(f"Output written to: {args.output_file}", file=sys.stderr)
    else:
        # Ensure UTF-8 output on Windows
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        print(output)


if __name__ == "__main__":
    main()
