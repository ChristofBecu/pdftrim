"""PDF Document wrapper for enhanced document management."""

import fitz
from typing import List, Optional, Union, TYPE_CHECKING
from pathlib import Path
from .page import Page

if TYPE_CHECKING:
    from types import TracebackType


class PDFDocument:
    """Wrapper class for PyMuPDF document objects with enhanced functionality."""
    
    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        """
        Initialize PDF document wrapper.
        
        Args:
            file_path: Path to PDF file, or None to create empty document
        """
        self.file_path = str(file_path) if file_path else None
        self._doc: Optional[fitz.Document] = None
        self._is_open = False
        
        if file_path:
            self.open(file_path)
        else:
            # Create empty document
            self._doc = fitz.open()  # Creates empty document
            self._is_open = True
    
    def open(self, file_path: Union[str, Path]) -> 'PDFDocument':
        """
        Open a PDF document from file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Self for method chaining
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If document cannot be opened
        """
        file_path = str(file_path)
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            if self._doc and self._is_open:
                self.close()
            
            self._doc = fitz.open(file_path)
            self.file_path = file_path
            self._is_open = True
            return self
        except Exception as e:
            raise Exception(f"Failed to open PDF document: {e}")
    
    def close(self) -> None:
        """Close the PDF document and free resources."""
        if self._doc and self._is_open:
            self._doc.close()
            self._is_open = False
    
    def save(self, output_path: Union[str, Path]) -> None:
        """
        Save the PDF document to a file.
        
        Args:
            output_path: Path where to save the document
        """
        if self._doc is None or not self._is_open:
            raise RuntimeError("Document is not open")
        
        self._doc.save(str(output_path))
    
    def __enter__(self) -> 'PDFDocument':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], 
                 exc_tb: Optional['TracebackType']) -> None:
        """Context manager exit - ensures document is closed."""
        self.close()
    
    def __len__(self) -> int:
        """Get number of pages in document."""
        if self._doc is None or not self._is_open:
            return 0
        return len(self._doc)
    
    def __getitem__(self, page_num: int) -> Page:
        """
        Get a specific page wrapped in Page class.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Page wrapper object
        """
        if self._doc is None or not self._is_open:
            raise RuntimeError("Document is not open")
        
        if page_num < 0 or page_num >= len(self._doc):
            raise IndexError(f"Page {page_num} out of range (0-{len(self._doc)-1})")
        
        fitz_page = self._doc[page_num]
        # Import config here to avoid circular imports
        from ..config.settings import config
        from ..ui.display import DisplayManager, DisplayConfig
        display = DisplayManager(DisplayConfig(debug_enabled=config.debug_mode))
        return Page(fitz_page, debug=config.debug_mode, display=display)
    
    def get_page(self, page_num: int) -> Page:
        """
        Get a specific page wrapped in Page class.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Page wrapper object
        """
        return self[page_num]
    
    def insert_pdf(self, other_doc: "PDFDocument", start_at: int = 0, 
                   from_page: int = 0, to_page: int = -1) -> None:
        """
        Insert pages from another PDF document.
        
        Args:
            other_doc: Another PDFDocument to insert pages from
            start_at: Page number to start inserting at (default: 0)
            from_page: First page to copy from other document (default: 0)
            to_page: Last page to copy from other document (default: -1 for all)
        """
        if self._doc is None or not self._is_open:
            raise RuntimeError("Document is not open")
        
        if other_doc._doc is None:
            raise RuntimeError("Source document is not open")
        
        self._doc.insert_pdf(other_doc._doc, start_at=start_at, 
                            from_page=from_page, to_page=to_page)
    
    def new_page(self, width: float = 595, height: float = 842) -> fitz.Page:
        """
        Create a new page in the document.
        
        Args:
            width: Page width in points (default A4 width)
            height: Page height in points (default A4 height)
            
        Returns:
            PyMuPDF page object
        """
        if self._doc is None or not self._is_open:
            raise RuntimeError("Document is not open")
        
        return self._doc.new_page(width=width, height=height)  # type: ignore[attr-defined]
    
    def delete_page(self, page_num: int) -> None:
        """
        Delete a page from the document.
        
        Args:
            page_num: Page number to delete (0-indexed)
        """
        if self._doc is None or not self._is_open:
            raise RuntimeError("Document is not open")
        
        if page_num < 0 or page_num >= len(self._doc):
            raise IndexError(f"Page {page_num} out of range (0-{len(self._doc)-1})")
        
        self._doc.delete_page(page_num)
    
    def search_text(self, text: str) -> List[tuple[int, float]]:
        """
        Search for text across all pages in the document.
        
        Args:
            text: Text to search for
            
        Returns:
            List of (page_number, y_coordinate) tuples where text was found
        """
        if self._doc is None or not self._is_open:
            raise RuntimeError("Document is not open")
        
        results = []
        for page_num in range(len(self._doc)):
            fitz_page = self._doc[page_num]  # Get raw fitz page
            text_instances = fitz_page.search_for(text)  # type: ignore[attr-defined]
            
            if text_instances:
                y_coord = text_instances[0].y0  # Top Y coordinate of first occurrence
                results.append((page_num, y_coord))
        
        return results
    
    def find_first_text_position(self, text: str) -> Optional[tuple[int, float]]:
        """
        Find the first occurrence of text in the document.
        
        Args:
            text: Text to search for
            
        Returns:
            (page_number, y_coordinate) tuple or None if not found
        """
        results = self.search_text(text)
        return results[0] if results else None
    
    def get_pages(self) -> List[Page]:
        """
        Get all pages as Page wrapper objects.
        
        Returns:
            List of Page wrapper objects
        """
        if self._doc is None or not self._is_open:
            return []
        
        # Import config here to avoid circular imports
        from ..config.settings import config
        from ..ui.display import DisplayManager, DisplayConfig
        display = DisplayManager(DisplayConfig(debug_enabled=config.debug_mode))
        return [Page(self._doc[i], debug=config.debug_mode, display=display) for i in range(len(self._doc))]
    
    @property
    def is_open(self) -> bool:
        """Check if document is currently open."""
        return self._is_open
    
    @property
    def page_count(self) -> int:
        """Get number of pages in document."""
        return len(self)
    
    def __repr__(self) -> str:
        """String representation of the PDF document."""
        status = "open" if self._is_open else "closed"
        pages = len(self) if self._is_open else "unknown"
        path = self.file_path or "empty document"
        return f"PDFDocument(path='{path}', pages={pages}, status={status})"