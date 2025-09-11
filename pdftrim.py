#!/usr/bin/env python3
"""
PDF Trimmer - Removes pages from a PDF starting at a specific search string.
"""

import sys
import os
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

# Configuration
DEBUG = False


def extract_page_text(page_layout) -> list[str]:
    """Extract text lines from a PDF page layout."""
    lines = []
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                line_text = text_line.get_text().strip()
                if line_text:
                    lines.append(line_text)
    return lines


def debug_pdfminer_first_lines(input_file: str) -> None:
    """Debug function to print the first line of each page."""
    if not DEBUG:
        return
        
    print("[DEBUG] Using pdfminer.six to extract first line of each page:")
    for page_num, page_layout in enumerate(extract_pages(input_file)):
        lines = extract_page_text(page_layout)
        first_line = lines[0] if lines else "[NO TEXT]"
        print(f"[DEBUG] pdfminer page {page_num}: {first_line}")


def find_cutoff_page_pdfminer(input_file: str, search_string: str) -> int | None:
    """
    Find the page number where the search string first appears.
    Returns the page number (0-indexed) or None if not found.
    """
    if DEBUG:
        print(f"[DEBUG] Using pdfminer.six to find cutoff page for: '{search_string}'")
    
    for page_num, page_layout in enumerate(extract_pages(input_file)):
        lines = extract_page_text(page_layout)
        page_text = '\n'.join(lines)
        first_line = lines[0] if lines else "[NO TEXT]"
        
        if DEBUG:
            print(f"[DEBUG] pdfminer page {page_num}: {first_line}")
        
        if search_string in page_text:
            if DEBUG:
                print(f"[DEBUG] pdfminer found search string on page {page_num}")
            return page_num
    
    if DEBUG:
        print(f"[DEBUG] pdfminer did not find search string; keeping all pages")
    return None


def create_output_filename(input_file: str) -> str:
    """Generate output filename by adding '_edit' suffix."""
    base, ext = os.path.splitext(input_file)
    return f"{base}_edit{ext}"


def trim_pdf(input_file: str, search_string: str) -> None:
    """
    Trim PDF by removing all pages starting from where search_string is found.
    
    Args:
        input_file: Path to input PDF file
        search_string: String to search for as cutoff point
    """
    if DEBUG:
        print(f"[DEBUG] Input file: {input_file}")
        print(f"[DEBUG] Search string: '{search_string}'")
    
    # Load PDF
    reader = PdfReader(input_file)
    if DEBUG:
        print(f"[DEBUG] Number of pages in PDF: {len(reader.pages)}")
    
    writer = PdfWriter()
    
    # Find where to cut off
    cutoff_page = find_cutoff_page_pdfminer(input_file, search_string)
    if cutoff_page is None:
        cutoff_page = len(reader.pages)
    
    if DEBUG:
        print(f"[DEBUG] Final cutoff_page: {cutoff_page}")
    
    # Copy pages up to cutoff
    for i in range(cutoff_page):
        if DEBUG:
            print(f"[DEBUG] Adding page {i} to output PDF")
        writer.add_page(reader.pages[i])
    
    # Create output filename and save
    output_file = create_output_filename(input_file)
    if DEBUG:
        print(f"[DEBUG] Output file will be: {output_file}")
    
    with open(output_file, "wb") as f:
        if DEBUG:
            print(f"[DEBUG] Writing output PDF...")
        writer.write(f)
    
    print(f"Saved trimmed PDF as: {output_file}")


def parse_arguments() -> tuple[str, str]:
    """Parse and validate command line arguments."""
    if len(sys.argv) != 3:
        print("Usage: python pdftrim.py input.pdf 'search_string'")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    search_str = sys.argv[2]
    
    # Validate input file exists
    if not os.path.exists(input_pdf):
        print(f"Error: Input file '{input_pdf}' does not exist.")
        sys.exit(1)
    
    return input_pdf, search_str


def main() -> None:
    """Main entry point."""
    input_pdf, search_str = parse_arguments()
    # debug_pdfminer_first_lines(input_pdf)  # Uncomment for debugging
    trim_pdf(input_pdf, search_str)




if __name__ == "__main__":
    main()
