#!/usr/bin/env python3
"""
PDF Trimmer - Removes pages from a PDF starting at a specific search string.
"""

import sys
import os
import glob
from pathlib import Path
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


def create_output_filename(input_file: str, output_dir: str) -> str:
    """Generate output filename in the specified output directory."""
    filename = os.path.basename(input_file)
    base, ext = os.path.splitext(filename)
    return os.path.join(output_dir, f"{base}_edit{ext}")


def ensure_output_directory(output_dir: str) -> None:
    """Create output directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")


def find_pdf_files(directory: str = ".") -> list[str]:
    """Find all PDF files in the given directory."""
    pdf_pattern = os.path.join(directory, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    return [f for f in pdf_files if not f.endswith("_edit.pdf")]  # Skip already processed files


def trim_pdf(input_file: str, search_string: str, output_dir: str) -> bool:
    """
    Trim PDF by removing all pages starting from where search_string is found.
    
    Args:
        input_file: Path to input PDF file
        search_string: String to search for as cutoff point
        output_dir: Directory to save the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if DEBUG:
            print(f"[DEBUG] Processing: {input_file}")
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
        output_file = create_output_filename(input_file, output_dir)
        if DEBUG:
            print(f"[DEBUG] Output file will be: {output_file}")
        
        with open(output_file, "wb") as f:
            if DEBUG:
                print(f"[DEBUG] Writing output PDF...")
            writer.write(f)
        
        print(f"✓ Processed: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {os.path.basename(input_file)}: {e}")
        return False


def parse_arguments() -> tuple[str, str]:
    """Parse and validate command line arguments."""
    if len(sys.argv) not in [2, 3]:
        print("Usage:")
        print("  python pdftrim.py 'search_string'                    # Process all PDFs in current directory")
        print("  python pdftrim.py input.pdf 'search_string'          # Process single PDF")
        print("  Output files will be saved in 'output' directory")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Process all PDFs in current directory
        return ".", sys.argv[1]
    else:
        # Process single PDF
        input_pdf = sys.argv[1]
        search_str = sys.argv[2]
        
        # Validate input file exists
        if not os.path.exists(input_pdf):
            print(f"Error: Input file '{input_pdf}' does not exist.")
            sys.exit(1)
        
        return input_pdf, search_str


def process_all_pdfs(search_string: str, output_dir: str = "output") -> None:
    """Process all PDF files in the current directory."""
    pdf_files = find_pdf_files()
    
    if not pdf_files:
        print("No PDF files found in current directory.")
        return
    
    ensure_output_directory(output_dir)
    
    print(f"Found {len(pdf_files)} PDF file(s) to process:")
    for pdf_file in pdf_files:
        print(f"  - {os.path.basename(pdf_file)}")
    
    print(f"\nProcessing files with search string: '{search_string}'")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        if trim_pdf(pdf_file, search_string, output_dir):
            successful += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Processing complete: {successful} successful, {failed} failed")


def process_single_pdf(input_pdf: str, search_string: str, output_dir: str = "output") -> None:
    """Process a single PDF file."""
    ensure_output_directory(output_dir)
    
    print(f"Processing: {os.path.basename(input_pdf)}")
    print(f"Search string: '{search_string}'")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    if trim_pdf(input_pdf, search_string, output_dir):
        print("-" * 50)
        print("Processing complete: 1 successful, 0 failed")
    else:
        print("-" * 50)
        print("Processing complete: 0 successful, 1 failed")


def main() -> None:
    """Main entry point."""
    input_arg, search_str = parse_arguments()
    
    if input_arg == ".":
        # Process all PDFs in current directory
        process_all_pdfs(search_str)
    else:
        # Process single PDF
        process_single_pdf(input_arg, search_str)




if __name__ == "__main__":
    main()
