#!/usr/bin/env python
"""
Generate ERD diagrams from Graphviz DOT file.

This script reads the ghfdb-erd.dot file and generates multiple output formats:
- PNG (raster image)
- SVG (vector image, web-friendly)
- PDF (vector image, print-friendly)

Usage:
    poetry run python docs/data_models/generate_erd.py

Requirements:
    - graphviz Python package (installed via: poetry run pip install graphviz)
    - Graphviz system binaries (dot, etc.) must be installed and in PATH
"""

from pathlib import Path

import graphviz


def generate_erd(dot_file: Path, output_dir: Path | None = None) -> None:
    """
    Generate ERD diagrams from a DOT file.

    Args:
        dot_file: Path to the .dot file
        output_dir: Directory to save output files (defaults to dot_file parent)
    """
    if output_dir is None:
        output_dir = dot_file.parent

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read the DOT file content
    dot_content = dot_file.read_text(encoding="utf-8")

    # Create a Graphviz Source object
    source = graphviz.Source(dot_content)

    # Base filename (without extension)
    base_name = dot_file.stem

    # Generate different formats
    formats = {
        "png": "PNG raster image (300 DPI)",
        "svg": "SVG vector image (web-friendly)",
        "pdf": "PDF vector image (print-ready)",
    }

    print(f"\nGenerating ERD diagrams from {dot_file.name}...")
    print(f"Output directory: {output_dir}\n")

    for fmt, description in formats.items():
        output_path = output_dir / f"{base_name}.{fmt}"
        print(f"Generating {description}...")
        try:
            # Render the diagram (DPI handled in DOT file or via engine args)
            source.format = fmt
            source.render(
                filename=base_name,
                directory=output_dir,
                format=fmt,
                cleanup=True,  # Remove intermediate file
            )
            print(f"  ✓ Created: {output_path}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            if "failed to execute" in str(e).lower() or "command not found" in str(e).lower():
                print("\n⚠️  Graphviz binaries not found!")
                print("Please install Graphviz system package:")
                print("  Windows: Download from https://graphviz.org/download/")
                print("  macOS:   brew install graphviz")
                print("  Linux:   sudo apt-get install graphviz")
                break

    print("\n✅ Done!")


if __name__ == "__main__":
    # Get the script directory
    script_dir = Path(__file__).parent

    # Path to the DOT file
    dot_file = script_dir / "ghfdb-erd.dot"

    if not dot_file.exists():
        print(f"❌ Error: DOT file not found: {dot_file}")
        exit(1)

    # Generate diagrams
    generate_erd(dot_file)
