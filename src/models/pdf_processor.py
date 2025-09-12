"""
PDF processor for handling the complete trimming workflow.

This module provides the PDFProcessor class that orchestrates the entire PDF
trimming workflow, coordinating between text finding and page manipulation.
"""

import os
from typing import Optional, Tuple, Union
from pathlib import Path
import fitz  # PyMuPDF

from .pdf_document import PDFDocument
from .text_search_engine import TextSearchEngine
from ..config.settings import config
from ..utils.file_manager import FileManager, FileValidationError
from ..ui.display_manager import DisplayManager, DisplayConfig


class ProcessingResult:
    """
    Result object for PDF processing operations.
    
    Contains information about the processing outcome including success status,
    output file path, and details about what operations were performed.
    """
    
    def __init__(self, success: bool, input_file: str, output_file: str = "", 
                 message: str = "", pages_trimmed: bool = False, 
                 blank_pages_removed: int = 0, trim_page: Optional[int] = None):
        self.success = success
        self.input_file = input_file
        self.output_file = output_file
        self.message = message
        self.pages_trimmed = pages_trimmed
        self.blank_pages_removed = blank_pages_removed
        self.trim_page = trim_page
    
    def __str__(self) -> str:
        """String representation for easy display."""
        if self.success:
            return f"✓ Processed: {os.path.basename(self.input_file)} -> {os.path.basename(self.output_file)} {self.message}"
        else:
            return f"✗ Error processing {os.path.basename(self.input_file)}: {self.message}"


class PDFProcessor:
    """
    A class for orchestrating PDF trimming operations.
    
    This class coordinates between text searching, page manipulation, and blank page
    removal to provide a complete PDF trimming workflow.
    """
    
    def __init__(self, debug: Optional[bool] = None, display_manager: Optional[DisplayManager] = None):
        """
        Initialize the PDFProcessor.
        
        Args:
            debug: Enable debug logging (defaults to config.debug_mode if None)
            display_manager: Optional DisplayManager for output formatting
        """
        self.debug = debug if debug is not None else config.debug_mode
        
        # Use provided DisplayManager or create a default one
        if display_manager:
            self.display = display_manager
        else:
            display_config = DisplayConfig(debug_enabled=self.debug)
            self.display = DisplayManager(display_config)
        
        # Initialize other components with shared DisplayManager
        self.search_engine = TextSearchEngine(debug=self.debug, display_manager=self.display)
        self.file_manager = FileManager(debug=self.debug, display_manager=self.display)
    
    def process_pdf(self, input_file: Union[str, Path], search_string: str, 
                   output_dir: Union[str, Path]) -> ProcessingResult:
        """
        Process a PDF file with trimming based on search string.
        
        Args:
            input_file: Path to input PDF file
            search_string: String to search for as cutoff point
            output_dir: Directory to save the output file
            
        Returns:
            ProcessingResult object with details about the operation
        """
        try:
            # Validate input file using FileManager
            validated_input = self.file_manager.validate_input_file(input_file)
            validated_output_dir = self.file_manager.ensure_output_directory(output_dir)
            
            self.display.debug(f"Processing: {validated_input}")
            self.display.debug(f"Search string: '{search_string}'")
            
            # Find the position of the search string
            position_result = self.search_engine.find_text_position(validated_input, search_string)
            
            # Generate output filename using FileManager
            output_file = self.file_manager.create_output_filename(validated_input, validated_output_dir)
            
            if position_result is None:
                # Search string not found - copy entire PDF but remove blank pages
                return self._process_without_trimming(validated_input, output_file)
            else:
                # Search string found - trim at that position
                page_num, y_coord = position_result
                return self._process_with_trimming(validated_input, output_file, page_num, y_coord)
                
        except FileValidationError as e:
            return ProcessingResult(
                success=False,
                input_file=str(input_file),
                message=str(e)
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_file=str(input_file),
                message=str(e)
            )
    
    def _process_without_trimming(self, input_file: str, output_file: str) -> ProcessingResult:
        """
        Process PDF without trimming - just remove blank pages.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            
        Returns:
            ProcessingResult object
        """
        self.display.debug("Search string not found, copying entire PDF and removing blank pages")
        
        with PDFDocument(input_file) as doc:
            blank_pages_removed = self._remove_blank_pages(doc)
            doc.save(output_file)
        
        if blank_pages_removed > 0:
            message = f"(no trim needed, removed {blank_pages_removed} blank page(s))"
        else:
            message = "(no changes needed)"
        
        return ProcessingResult(
            success=True,
            input_file=input_file,
            output_file=output_file,
            message=message,
            pages_trimmed=False,
            blank_pages_removed=blank_pages_removed
        )
    
    def _process_with_trimming(self, input_file: str, output_file: str, 
                              page_num: int, y_coord: float) -> ProcessingResult:
        """
        Process PDF with trimming at specified page and coordinate.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            page_num: Page number where trimming should occur (0-indexed)
            y_coord: Y-coordinate for trimming cutoff
            
        Returns:
            ProcessingResult object
        """
        self.display.debug(f"Will trim page {page_num} at Y-coordinate {y_coord}")
        
        blank_pages_removed = self._trim_page_content(input_file, output_file, page_num, y_coord)
        
        message = f"(trimmed at page {page_num + 1}, blank pages removed)"
        
        return ProcessingResult(
            success=True,
            input_file=input_file,
            output_file=output_file,
            message=message,
            pages_trimmed=True,
            blank_pages_removed=blank_pages_removed,
            trim_page=page_num + 1  # 1-indexed for user display
        )
    
    def _trim_page_content(self, input_file: str, output_file: str, 
                          page_num: int, y_cutoff: float) -> int:
        """
        Trim content from a specific page at the given Y-coordinate.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            page_num: Page number to trim (0-indexed)
            y_cutoff: Y-coordinate cutoff point
            
        Returns:
            Number of blank pages removed
        """
        with PDFDocument(input_file) as source_doc:
            with PDFDocument() as new_doc:  # Create empty document
                
                # Copy all pages before the cutoff page
                for i in range(page_num):
                    # Insert each page at the end to maintain order
                    new_doc.insert_pdf(source_doc, start_at=len(new_doc), from_page=i, to_page=i)
                
                # Process the cutoff page - remove content below y_cutoff
                if page_num < len(source_doc):
                    source_page = source_doc[page_num]
                    page_rect = source_page.rect
                    
                    # Create a clipping rectangle that keeps only content above y_cutoff
                    clip_rect = fitz.Rect(page_rect.x0, page_rect.y0, page_rect.x1, y_cutoff)
                    
                    # Create a new page in the output document
                    new_page = new_doc.new_page(width=page_rect.width, height=page_rect.height)
                    
                    # Copy the page content but clip it to remove content below y_cutoff
                    new_page.show_pdf_page(new_page.rect, source_doc._doc, page_num, clip=clip_rect)
                
                # Remove blank pages from the final document
                blank_pages_removed = self._remove_blank_pages(new_doc)
                
                if blank_pages_removed > 0:
                    self.display.debug(f"Removed {blank_pages_removed} blank page(s)")
                
                # Save the modified document
                new_doc.save(output_file)
                
                return blank_pages_removed
    
    def _remove_blank_pages(self, doc: PDFDocument) -> int:
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
                self.display.debug(f"Found blank page: {page_num}")
        
        # Remove blank pages
        for page_num in blank_pages:
            doc.delete_page(page_num)
            self.display.debug(f"Removed blank page: {page_num}")
        
        return len(blank_pages)
    

    def batch_process(self, input_files: list[Union[str, Path]], search_string: str, 
                     output_dir: Union[str, Path]) -> list[ProcessingResult]:
        """
        Process multiple PDF files in batch.
        
        Args:
            input_files: List of input PDF file paths
            search_string: String to search for as cutoff point
            output_dir: Directory to save the output files
            
        Returns:
            List of ProcessingResult objects for each file
        """
        results = []
        
        for input_file in input_files:
            result = self.process_pdf(input_file, search_string, output_dir)
            results.append(result)
        
        return results
    
    def get_processing_stats(self, results: list[ProcessingResult]) -> dict:
        """
        Get statistics from processing results.
        
        Args:
            results: List of ProcessingResult objects
            
        Returns:
            Dictionary with processing statistics
        """
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        trimmed = sum(1 for r in results if r.success and r.pages_trimmed)
        total_blank_pages = sum(r.blank_pages_removed for r in results if r.success)
        
        return {
            'total_files': len(results),
            'successful': successful,
            'failed': failed,
            'files_trimmed': trimmed,
            'files_blank_only': successful - trimmed,
            'total_blank_pages_removed': total_blank_pages
        }