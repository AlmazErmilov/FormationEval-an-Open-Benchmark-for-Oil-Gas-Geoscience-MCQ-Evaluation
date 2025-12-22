#!/usr/bin/env python3
"""
Convert PDF to Markdown using Mistral OCR API.

Uses mistral-ocr-latest model for document understanding.
Supports single files and batch processing of directories.

Usage:
    python src/pdf_to_markdown.py <pdf_path> [output_path]
    python src/pdf_to_markdown.py --batch <input_dir> [--output-dir <output_dir>]

Requirements:
    pip install mistralai python-dotenv
    Set MISTRAL_API_KEY in .env file

Limits:
    - Max file size: 50MB
    - Max pages per file: 1000
    - Cost: ~$1 per 1000 pages
"""

import argparse
import base64
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")


def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    table_format: str = "markdown",
    include_images: bool = False,
    verbose: bool = True
) -> str:
    """
    Convert a PDF file to Markdown using Mistral OCR.

    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path for output markdown file
        table_format: Table output format - "markdown" or "html"
        include_images: Whether to embed base64 images in output
        verbose: Whether to print progress messages

    Returns:
        The extracted markdown content
    """
    # Import here to fail gracefully if not installed
    try:
        from mistralai import Mistral
    except ImportError:
        raise ImportError("mistralai package not installed. Run: pip install mistralai")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in environment variables. Add it to .env file.")

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Check file size (max 50MB for Mistral OCR)
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if verbose:
        print(f"File: {pdf_path.name} ({file_size_mb:.2f} MB)")

    if file_size_mb > 50:
        raise ValueError(f"PDF file too large ({file_size_mb:.2f} MB). Maximum is 50 MB.")

    # Read and encode PDF as base64
    with open(pdf_path, "rb") as f:
        pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

    if verbose:
        print("Calling Mistral OCR API...")

    client = Mistral(api_key=api_key)

    # Call OCR endpoint with base64 data URL
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{pdf_data}",
        },
        table_format=table_format,
        include_image_base64=include_images,
    )

    # Extract markdown from response
    markdown_content = ""

    if hasattr(ocr_response, 'pages') and ocr_response.pages:
        page_count = len(ocr_response.pages)
        if verbose:
            print(f"Extracted {page_count} pages")

        for i, page in enumerate(ocr_response.pages):
            if hasattr(page, 'markdown') and page.markdown:
                markdown_content += page.markdown + "\n\n"
            if verbose and (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{page_count} pages...")

    elif hasattr(ocr_response, 'text'):
        markdown_content = ocr_response.text
    else:
        markdown_content = str(ocr_response)

    # Clean up trailing whitespace
    markdown_content = markdown_content.strip() + "\n"

    # Save to file if output path specified
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        if verbose:
            print(f"Saved: {output_path} ({len(markdown_content):,} chars)")

    return markdown_content


def batch_convert(
    input_dir: str,
    output_dir: Optional[str] = None,
    table_format: str = "markdown",
    include_images: bool = False,
    verbose: bool = True
) -> list[tuple[str, str]]:
    """
    Convert all PDFs in a directory to Markdown.

    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory for output files (default: same as input)
        table_format: Table output format - "markdown" or "html"
        include_images: Whether to embed base64 images
        verbose: Whether to print progress messages

    Returns:
        List of (pdf_path, md_path) tuples for successfully converted files
    """
    input_dir = Path(input_dir)
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_dir}")

    output_dir = Path(output_dir) if output_dir else input_dir

    # Find all PDF files
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return []

    if verbose:
        print(f"Found {len(pdf_files)} PDF files in {input_dir}")
        print("-" * 60)

    results = []
    for i, pdf_path in enumerate(pdf_files, 1):
        if verbose:
            print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")

        # Output path: same name with .md extension
        md_path = output_dir / f"{pdf_path.stem}.md"

        try:
            convert_pdf_to_markdown(
                pdf_path=str(pdf_path),
                output_path=str(md_path),
                table_format=table_format,
                include_images=include_images,
                verbose=verbose
            )
            results.append((str(pdf_path), str(md_path)))
        except Exception as e:
            print(f"  ERROR: {e}")

    if verbose:
        print("\n" + "=" * 60)
        print(f"Converted {len(results)}/{len(pdf_files)} files successfully")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown using Mistral OCR API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/pdf_to_markdown.py document.pdf
  python src/pdf_to_markdown.py document.pdf output.md
  python src/pdf_to_markdown.py --batch ./pdfs/
  python src/pdf_to_markdown.py --batch ./pdfs/ --output-dir ./markdown/
        """
    )

    parser.add_argument(
        "input",
        help="PDF file path, or directory path when using --batch"
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="Output markdown file path (default: same name with .md extension)"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all PDFs in a directory"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for batch processing (default: same as input)"
    )
    parser.add_argument(
        "--table-format",
        choices=["markdown", "html"],
        default="markdown",
        help="Table output format (default: markdown)"
    )
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Embed base64 images in output (increases file size)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress messages"
    )

    args = parser.parse_args()

    try:
        if args.batch:
            batch_convert(
                input_dir=args.input,
                output_dir=args.output_dir,
                table_format=args.table_format,
                include_images=args.include_images,
                verbose=not args.quiet
            )
        else:
            output_path = args.output
            if not output_path:
                # Default: same directory, .md extension
                output_path = str(Path(args.input).with_suffix(".md"))

            convert_pdf_to_markdown(
                pdf_path=args.input,
                output_path=output_path,
                table_format=args.table_format,
                include_images=args.include_images,
                verbose=not args.quiet
            )

        print("\nDone!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
