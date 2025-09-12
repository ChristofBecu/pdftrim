#!/usr/bin/env python3
"""
PDF Trimmer - Removes pages from a PDF starting at a specific search string.
"""

from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextBox, LTTextLine, LTChar

# Import our custom classes
from src.models.pdf_document import PDFDocument
from src.models.pdf_processor import PDFProcessor
from src.cli.cli_handler import CLIHandler
from src.config.settings import config
from src.workflow.workflow_manager import WorkflowManager
from src.ui.display_manager import DisplayManager, DisplayConfig

# Initialize a global DisplayManager for functions that need debug output
display = DisplayManager(DisplayConfig(debug_enabled=config.debug_mode))


def trim_pdf(input_file: str, search_string: str, output_dir: str | None = None) -> bool:
    """
    Trim a PDF file by removing pages after the search string.
    
    Args:
        input_file: Path to the input PDF file
        search_string: Text to search for as the cutoff point
        output_dir: Directory to save the output file (optional)
        
    Returns:
        True if processing was successful, False otherwise
    """
    # Use WorkflowManager for consistent processing
    workflow = WorkflowManager(display=display, debug=config.debug_mode)
    return workflow.process_single_file(input_file, search_string, output_dir)


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
            display.debug(f"Found blank page: {page_num}")
    
    # Remove blank pages
    for page_num in blank_pages:
        doc.delete_page(page_num)
        display.debug(f"Removed blank page: {page_num}")
    
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
        
    display.debug("Using pdfminer.six to extract first line of each page:")
    for page_num, page_layout in enumerate(extract_pages(input_file)):
        lines = extract_page_text(page_layout)
        first_line = lines[0] if lines else "[NO TEXT]"
        display.debug(f"pdfminer page {page_num}: {first_line}")


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
    
    # Display the result
    if result.success and result.output_file:
        display.file_processing_result(str(input_file), str(result.output_file), "Success")
    else:
        display.error(result.message)
    
    return result.success


def process_all_pdfs(search_string: str, output_dir: str | None = None) -> None:
    """Process all PDF files in the current directory."""
    # Use WorkflowManager for consistent processing
    workflow = WorkflowManager(display=display, debug=config.debug_mode)
    workflow.process_batch(search_string, output_dir)


def process_single_pdf(input_pdf: str, search_string: str, output_dir: str | None = None) -> None:
    """Process a single PDF file."""
    # Use WorkflowManager for consistent processing
    workflow = WorkflowManager(display=display, debug=config.debug_mode)
    workflow.process_single_file(input_pdf, search_string, output_dir)


def main() -> None:
    """Main entry point."""
    # Initialize CLI handler
    cli_handler = CLIHandler(debug=config.debug_mode, display=display)
    
    # Parse command line arguments
    args = cli_handler.handle_arguments()
    
    # Use WorkflowManager for processing
    workflow = WorkflowManager(display=display, debug=config.debug_mode)
    workflow.process_workflow(
        input_path=args.input_path if not args.is_batch_mode else None,
        search_string=args.search_string,
        output_dir=args.output_dir,
        is_batch_mode=args.is_batch_mode
    )




if __name__ == "__main__":
    main()
