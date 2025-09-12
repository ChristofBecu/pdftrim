"""Page model for PDF processing."""

import fitz
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fitz import Page as FitzPage


class Page:
    """Wrapper class for PyMuPDF page objects with enhanced functionality."""
    
    def __init__(self, fitz_page: Any, debug: bool = False):
        """
        Initialize Page wrapper.
        
        Args:
            fitz_page: PyMuPDF page object
            debug: Enable debug logging
        """
        self._page = fitz_page
        self.debug = debug
    
    @property
    def rect(self):
        """Get page rectangle."""
        return self._page.rect
    
    def get_text(self, option: str = "text") -> str:
        """Get text content from page."""
        return self._page.get_text(option)
    
    def get_drawings(self) -> list:
        """Get drawing objects from page."""
        return self._page.get_drawings()
    
    def get_images(self) -> list:
        """Get image objects from page."""
        return self._page.get_images()
    
    def search_for(self, text: str) -> list:
        """Search for text on page."""
        return self._page.search_for(text)
    
    def show_pdf_page(self, *args, **kwargs):
        """Show PDF page content."""
        return self._page.show_pdf_page(*args, **kwargs)
    
    def is_blank(self) -> bool:
        """
        Check if page is blank or contains only decorative content without meaningful text.
        
        Returns:
            True if the page is blank, False otherwise
        """
        # Get all text from the page
        text = self.get_text().strip()
        meaningful_text = text.replace(' ', '').replace('\n', '').replace('\t', '')
        
        # If there's substantial meaningful text content, it's definitely not blank
        if len(meaningful_text) > 20:
            return False
        
        # Check for text blocks - more reliable than raw text
        text_blocks = self.get_text('blocks')
        substantial_text_blocks = [block for block in text_blocks if len(block[4].strip()) > 10]
        
        if substantial_text_blocks:
            if self.debug:
                print(f"[DEBUG] Page has {len(substantial_text_blocks)} substantial text blocks")
            return False
        
        # Get page dimensions for analysis
        rect = self.rect
        drawings = self.get_drawings()
        images = self.get_images()
        
        # Special case: if there's no text AND it's likely a template/decorative page
        if len(meaningful_text) == 0:
            # Even with images/drawings, if there's absolutely no text, 
            # it's likely a blank template page
            if self.debug:
                print(f"[DEBUG] Page has no text content - Text: '{text}', Drawings: {len(drawings)}, Images: {len(images)}")
            return True
        
        # If there's minimal text (1-20 chars), check if it's just page numbers or similar
        if len(meaningful_text) <= 20:
            # Check if the text is just numbers, dates, or other minimal content
            if text.replace(' ', '').replace('\n', '').isdigit() or len(text.strip()) < 5:
                if self.debug:
                    print(f"[DEBUG] Page has only minimal text content: '{text}'")
                return True
        
        # If we get here, there's some text content, so keep the page
        return False