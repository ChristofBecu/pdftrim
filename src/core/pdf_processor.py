"""
PDF processor for handling the complete trimming workflow.

This module provides the PDFProcessor class that orchestrates the entire PDF
trimming workflow, coordinating between text finding and page manipulation.
"""

from typing import Optional, Union
from pathlib import Path
import fitz  # PyMuPDF

from ..models.pdf_document import PDFDocument
from ..models.result import ProcessingResult
from .text_search import TextSearchEngine
from .page_spec import (
    PageSpecError,
    parse_delete_spec,
    compute_indices_to_delete,
    indices_before_page,
    indices_after_page,
)
from ..config.settings import config
from ..services.file_service import FileService, FileValidationError
from ..ui.display import DisplayManager, DisplayConfig
from ..di.interfaces import IPDFProcessor


class PDFProcessor(IPDFProcessor):
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
        self.file_manager = FileService(debug=self.debug, display_manager=self.display)
    
    def process_pdf(self, input_file: Union[str, Path], search_string: str, 
                   output_dir: Union[str, Path],
                   invert_selection: bool = False) -> ProcessingResult:
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
                return self._process_without_trimming(validated_input, output_file, invert_selection=invert_selection)
            else:
                # Search string found - trim at that position
                page_num, y_coord = position_result
                return self._process_with_trimming(
                    validated_input,
                    output_file,
                    page_num,
                    y_coord,
                    invert_selection=invert_selection,
                )
                
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

    def process_pdf_delete_pages(self, input_file: Union[str, Path], delete_spec: str,
                                output_dir: Union[str, Path],
                                invert_selection: bool = False) -> ProcessingResult:
        """Delete specific pages/ranges from a PDF (1-based spec like '1-4,7').

        If invert_selection is True, delete_spec is interpreted as a keep
        specification (keep only those pages; delete all others).
        """
        try:
            validated_input = self.file_manager.validate_input_file(input_file)
            validated_output_dir = self.file_manager.ensure_output_directory(output_dir)
            output_file = self.file_manager.create_output_filename(validated_input, validated_output_dir)

            with PDFDocument(validated_input) as doc:
                page_count = len(doc)
                indices_to_delete, keep_indices_desc = compute_indices_to_delete(
                    delete_spec,
                    page_count=page_count,
                    invert_selection=invert_selection,
                )

                if len(indices_to_delete) >= page_count:
                    return ProcessingResult(
                        success=False,
                        input_file=validated_input,
                        message="Deletion would remove all pages; refusing to create an empty PDF.",
                        operation="delete",
                        invert_selection=invert_selection,
                    )

                for idx in indices_to_delete:
                    doc.delete_page(idx)

                blank_pages_removed = self._remove_blank_pages(doc)
                doc.save(output_file)

            deleted_pages_1_based = sorted([i + 1 for i in indices_to_delete])

            if invert_selection:
                kept_pages_1_based = sorted([(i + 1) for i in (keep_indices_desc or [])])
                message = (
                    f"(kept {len(kept_pages_1_based)} page(s), deleted {len(deleted_pages_1_based)} page(s), "
                    f"removed {blank_pages_removed} blank page(s))"
                )
            else:
                message = f"(deleted {len(deleted_pages_1_based)} page(s), removed {blank_pages_removed} blank page(s))"

            return ProcessingResult(
                success=True,
                input_file=validated_input,
                output_file=output_file,
                message=message,
                pages_trimmed=False,
                blank_pages_removed=blank_pages_removed,
                operation="delete",
                pages_deleted=len(deleted_pages_1_based),
                deleted_pages=deleted_pages_1_based,
                delete_spec=None if invert_selection else delete_spec,
                invert_selection=invert_selection,
                keep_spec=delete_spec if invert_selection else None,
                kept_pages=kept_pages_1_based if invert_selection else None,
            )

        except (FileValidationError, PageSpecError) as e:
            message = str(e)
            if invert_selection:
                message = message.replace("Delete specification", "Keep specification")
                message = message.replace("delete specification", "keep specification")
                message = message.replace("Cannot delete pages", "Cannot keep pages")
            return ProcessingResult(
                success=False,
                input_file=str(input_file),
                message=message,
                operation="delete",
                delete_spec=None if invert_selection else delete_spec,
                invert_selection=invert_selection,
                keep_spec=delete_spec if invert_selection else None,
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_file=str(input_file),
                message=str(e),
                operation="delete",
                delete_spec=None if invert_selection else delete_spec,
                invert_selection=invert_selection,
                keep_spec=delete_spec if invert_selection else None,
            )

    def process_pdf_delete_before_after(self, input_file: Union[str, Path],
                                       before_page: Optional[int],
                                       after_page: Optional[int],
                                       output_dir: Union[str, Path],
                                       invert_selection: bool = False) -> ProcessingResult:
        """Delete pages before/after a 1-based page number.

        Rules:
        - before_page deletes 1..before_page-1
        - after_page deletes after_page+1..end
        - before_page and after_page may be combined
        """
        try:
            validated_input = self.file_manager.validate_input_file(input_file)
            validated_output_dir = self.file_manager.ensure_output_directory(output_dir)
            output_file = self.file_manager.create_output_filename(validated_input, validated_output_dir)

            with PDFDocument(validated_input) as doc:
                page_count = len(doc)
                indices: set[int] = set()

                if before_page is not None:
                    indices.update(indices_before_page(before_page_1_based=before_page, page_count=page_count))
                if after_page is not None:
                    indices.update(indices_after_page(after_page_1_based=after_page, page_count=page_count))

                base_indices_to_delete = sorted(indices, reverse=True)
                if invert_selection:
                    keep_set = set(base_indices_to_delete)
                    indices_to_delete = [
                        i for i in range(page_count - 1, -1, -1) if i not in keep_set
                    ]
                else:
                    indices_to_delete = base_indices_to_delete

                if page_count > 0 and len(indices_to_delete) >= page_count:
                    return ProcessingResult(
                        success=False,
                        input_file=validated_input,
                        message="Deletion would remove all pages; refusing to create an empty PDF.",
                        operation="before_after",
                        invert_selection=invert_selection,
                    )

                for idx in indices_to_delete:
                    doc.delete_page(idx)

                blank_pages_removed = self._remove_blank_pages(doc)
                doc.save(output_file)

            deleted_pages_1_based = sorted([i + 1 for i in indices_to_delete])
            if invert_selection:
                kept_pages_1_based = sorted([i + 1 for i in base_indices_to_delete])
                message = (
                    f"(kept {len(kept_pages_1_based)} page(s), deleted {len(deleted_pages_1_based)} page(s), "
                    f"removed {blank_pages_removed} blank page(s))"
                )
            else:
                message = f"(deleted {len(deleted_pages_1_based)} page(s), removed {blank_pages_removed} blank page(s))"

            return ProcessingResult(
                success=True,
                input_file=validated_input,
                output_file=output_file,
                message=message,
                pages_trimmed=False,
                blank_pages_removed=blank_pages_removed,
                operation="before_after",
                pages_deleted=len(deleted_pages_1_based),
                deleted_pages=deleted_pages_1_based,
                before_page=before_page,
                after_page=after_page,
                invert_selection=invert_selection,
                kept_pages=sorted([i + 1 for i in base_indices_to_delete]) if invert_selection else None,
            )

        except (FileValidationError, PageSpecError) as e:
            return ProcessingResult(
                success=False,
                input_file=str(input_file),
                message=str(e),
                operation="before_after",
                before_page=before_page,
                after_page=after_page,
                invert_selection=invert_selection,
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_file=str(input_file),
                message=str(e),
                operation="before_after",
                before_page=before_page,
                after_page=after_page,
                invert_selection=invert_selection,
            )
    
    def _process_without_trimming(self, input_file: str, output_file: str, *, invert_selection: bool) -> ProcessingResult:
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
            blank_pages_removed=blank_pages_removed,
            operation="search",
            search_found=False,
            invert_selection=invert_selection,
        )
    
    def _process_with_trimming(self, input_file: str, output_file: str, 
                              page_num: int, y_coord: float, *, invert_selection: bool) -> ProcessingResult:
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
        
        if invert_selection:
            blank_pages_removed = self._trim_page_content_inverted(input_file, output_file, page_num, y_coord)
            message = f"(trimmed (inverted) at page {page_num + 1}, blank pages removed)"
        else:
            blank_pages_removed = self._trim_page_content(input_file, output_file, page_num, y_coord)
            message = f"(trimmed at page {page_num + 1}, blank pages removed)"
        
        return ProcessingResult(
            success=True,
            input_file=input_file,
            output_file=output_file,
            message=message,
            pages_trimmed=True,
            blank_pages_removed=blank_pages_removed,
            trim_page=page_num + 1,  # 1-indexed for user display
            operation="search",
            search_found=True,
            invert_selection=invert_selection,
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

    def _trim_page_content_inverted(self, input_file: str, output_file: str,
                                   page_num: int, y_cutoff: float) -> int:
        """Inverted trim: keep content starting at the search location.

        This keeps the part of the match page *below* y_cutoff, plus all pages
        after that page.
        """

        with PDFDocument(input_file) as source_doc:
            with PDFDocument() as new_doc:
                if page_num < len(source_doc):
                    source_page = source_doc[page_num]
                    page_rect = source_page.rect

                    clip_rect = fitz.Rect(page_rect.x0, y_cutoff, page_rect.x1, page_rect.y1)

                    new_page = new_doc.new_page(width=page_rect.width, height=page_rect.height)
                    new_page.show_pdf_page(new_page.rect, source_doc._doc, page_num, clip=clip_rect)

                # Copy all pages after the cutoff page
                for i in range(page_num + 1, len(source_doc)):
                    new_doc.insert_pdf(source_doc, start_at=len(new_doc), from_page=i, to_page=i)

                blank_pages_removed = self._remove_blank_pages(new_doc)
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