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
from pdfminer.layout import LTTextContainer, LTTextBox, LTTextLine, LTChar
import fitz  # PyMuPDF for more advanced PDF manipulation

# Import our custom classes
from src.models.page import Page
from src.models.pdf_document import PDFDocument
from src.models.text_search_engine import TextSearchEngine
from src.models.pdf_processor import PDFProcessor
from src.config.settings import config

# Configuration is now handled by the config object


def remove_blank_pages(doc: PDFDocument) -> int:
    """
    Remove blank pages from a PDF document.
    
    Args:
        doc: A PDFDocument object
        
    Returns:
        Number of blank pages removed
    """
    blank_pages = []
    
    # Identify blank pages (iterate in reverse to avoid index issues when deleting)
    for page_num in range(len(doc) - 1, -1, -1):
        page = doc[page_num]
        if page.is_blank():
            blank_pages.append(page_num)
            if config.debug_mode:
                print(f"[DEBUG] Found blank page: {page_num}")
    
    # Remove blank pages
    for page_num in blank_pages:
        doc.delete_page(page_num)
        if config.debug_mode:
            print(f"[DEBUG] Removed blank page: {page_num}")
    
    return len(blank_pages)


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
    if not config.debug_mode:
        return
        
    print("[DEBUG] Using pdfminer.six to extract first line of each page:")
    for page_num, page_layout in enumerate(extract_pages(input_file)):
        lines = extract_page_text(page_layout)
        first_line = lines[0] if lines else "[NO TEXT]"
        print(f"[DEBUG] pdfminer page {page_num}: {first_line}")





def trim_pdf_advanced(input_file: str, search_string: str, output_dir: str) -> bool:
    """
    Advanced PDF trimming that can remove content from the middle of a page.
    
    Now uses the PDFProcessor class for improved workflow orchestration.
    
    Args:
        input_file: Path to input PDF file
        search_string: String to search for as cutoff point
        output_dir: Directory to save the output file
        
    Returns:
        True if successful, False otherwise
    """
    # Create PDF processor with debug mode from config
    processor = PDFProcessor(debug=config.debug_mode)
    
    # Process the PDF using the processor
    result = processor.process_pdf(input_file, search_string, output_dir)
    
    # Print the result
    print(result)
    
    return result.success





def find_pdf_files(directory: str = ".") -> list[str]:
    """Find all PDF files in the given directory."""
    pdf_pattern = os.path.join(directory, config.pdf_pattern)
    pdf_files = glob.glob(pdf_pattern)
    return [f for f in pdf_files if not f.endswith(config.processed_suffix)]  # Skip already processed files


def trim_pdf(input_file: str, search_string: str, output_dir: str) -> bool:
    """
    Trim PDF by removing content starting from where search_string is found.
    This version can trim content from the middle of a page.
    
    Args:
        input_file: Path to input PDF file
        search_string: String to search for as cutoff point
        output_dir: Directory to save the output file
        
    Returns:
        True if successful, False otherwise
    """
    return trim_pdf_advanced(input_file, search_string, output_dir)


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


def process_all_pdfs(search_string: str, output_dir: str | None = None) -> None:
    """Process all PDF files in the current directory."""
    if output_dir is None:
        output_dir = config.output_dir
        
    pdf_files = find_pdf_files()
    
    if not pdf_files:
        print("No PDF files found in current directory.")
        return
    
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


def process_single_pdf(input_pdf: str, search_string: str, output_dir: str | None = None) -> None:
    """Process a single PDF file."""
    if output_dir is None:
        output_dir = config.output_dir
        
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
