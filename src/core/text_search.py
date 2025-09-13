"""
Text search engine for PDF documents.

This module provides the TextSearchEngine class for handling all text searching logic
across PDF documents, including different search strategies and coordinate extraction.
"""

from typing import Optional, Tuple, Union
from pathlib import Path

from ..models.pdf_document import PDFDocument
from ..ui.display import DisplayManager, DisplayConfig
from ..di.interfaces import ITextSearchEngine


class TextSearchEngine(ITextSearchEngine):
    """
    A class for handling text search operations in PDF documents.
    
    This class encapsulates all text searching logic, providing methods for finding
    text positions, extracting coordinates, and implementing different search strategies.
    """
    
    def __init__(self, debug: bool = False, display_manager: Optional[DisplayManager] = None):
        """
        Initialize the TextSearchEngine.
        
        Args:
            debug: Enable debug logging for search operations
            display_manager: Optional DisplayManager for output formatting
        """
        self.debug = debug
        
        # Use provided DisplayManager or create a default one
        if display_manager:
            self.display = display_manager
        else:
            display_config = DisplayConfig(debug_enabled=self.debug)
            self.display = DisplayManager(display_config)
    
    def find_text_position(self, pdf_path: Union[str, Path], search_string: str) -> Optional[Tuple[int, float]]:
        """
        Find the first occurrence of text in a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            search_string: Text to search for
            
        Returns:
            Tuple of (page_number, y_coordinate) if found, None otherwise
        """
        self.display.debug(f"Using PyMuPDF to find text position for: '{search_string}'")
        
        with PDFDocument(pdf_path) as doc:
            result = doc.find_first_text_position(search_string)
            
            if result:
                page_num, y_coord = result
                self.display.debug(f"Found '{search_string}' on page {page_num} at Y-coordinate {y_coord}")
                return page_num, y_coord
            else:
                self.display.debug(f"Text '{search_string}' not found in document")
                return None