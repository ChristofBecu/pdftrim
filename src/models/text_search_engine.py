"""
Text search engine for PDF documents.

This module provides the TextSearchEngine class for handling all text searching logic
across PDF documents, including different search strategies and coordinate extraction.
"""

from typing import Optional, Tuple, List, Union
from pathlib import Path

from .pdf_document import PDFDocument


class TextSearchEngine:
    """
    A class for handling text search operations in PDF documents.
    
    This class encapsulates all text searching logic, providing methods for finding
    text positions, extracting coordinates, and implementing different search strategies.
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize the TextSearchEngine.
        
        Args:
            debug: Enable debug logging for search operations
        """
        self.debug = debug
    
    def find_text_position(self, pdf_path: Union[str, Path], search_string: str) -> Optional[Tuple[int, float]]:
        """
        Find the first occurrence of text in a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            search_string: Text to search for
            
        Returns:
            Tuple of (page_number, y_coordinate) if found, None otherwise
        """
        if self.debug:
            print(f"[DEBUG] Using PyMuPDF to find text position for: '{search_string}'")
        
        with PDFDocument(pdf_path) as doc:
            result = doc.find_first_text_position(search_string)
            
            if result:
                page_num, y_coord = result
                if self.debug:
                    print(f"[DEBUG] Found '{search_string}' on page {page_num} at Y-coordinate {y_coord}")
                return page_num, y_coord
            else:
                if self.debug:
                    print(f"[DEBUG] Text '{search_string}' not found in document")
                return None
    
    def find_all_text_positions(self, pdf_path: Union[str, Path], search_string: str) -> List[Tuple[int, float]]:
        """
        Find all occurrences of text in a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            search_string: Text to search for
            
        Returns:
            List of (page_number, y_coordinate) tuples for all occurrences
        """
        if self.debug:
            print(f"[DEBUG] Searching for all occurrences of: '{search_string}'")
        
        with PDFDocument(pdf_path) as doc:
            results = doc.search_text(search_string)
            
            if self.debug:
                if results:
                    print(f"[DEBUG] Found {len(results)} occurrence(s) of '{search_string}'")
                    for page_num, y_coord in results:
                        print(f"[DEBUG]   Page {page_num}: Y-coordinate {y_coord}")
                else:
                    print(f"[DEBUG] Text '{search_string}' not found in document")
            
            return results
    
    def find_text_on_page(self, pdf_path: Union[str, Path], search_string: str, page_num: int) -> List[float]:
        """
        Find all occurrences of text on a specific page.
        
        Args:
            pdf_path: Path to the PDF file
            search_string: Text to search for
            page_num: Page number to search (0-indexed)
            
        Returns:
            List of y-coordinates where text was found on the specified page
        """
        if self.debug:
            print(f"[DEBUG] Searching for '{search_string}' on page {page_num}")
        
        with PDFDocument(pdf_path) as doc:
            if page_num >= len(doc):
                if self.debug:
                    print(f"[DEBUG] Page {page_num} out of range (document has {len(doc)} pages)")
                return []
            
            page = doc[page_num]
            text_instances = page._page.search_for(search_string)
            
            y_coordinates = [rect.y0 for rect in text_instances]
            
            if self.debug:
                if y_coordinates:
                    print(f"[DEBUG] Found {len(y_coordinates)} occurrence(s) on page {page_num}")
                    for y_coord in y_coordinates:
                        print(f"[DEBUG]   Y-coordinate: {y_coord}")
                else:
                    print(f"[DEBUG] Text '{search_string}' not found on page {page_num}")
            
            return y_coordinates
    
    def search_with_strategy(self, pdf_path: Union[str, Path], search_string: str, 
                           strategy: str = "first") -> Optional[Tuple[int, float]]:
        """
        Search for text using different strategies.
        
        Args:
            pdf_path: Path to the PDF file
            search_string: Text to search for
            strategy: Search strategy ("first", "last", "highest", "lowest")
            
        Returns:
            Tuple of (page_number, y_coordinate) based on strategy, None if not found
        """
        all_results = self.find_all_text_positions(pdf_path, search_string)
        
        if not all_results:
            return None
        
        if strategy == "first":
            return all_results[0]
        elif strategy == "last":
            return all_results[-1]
        elif strategy == "highest":
            # Highest Y-coordinate (remember PDF coordinates start from bottom)
            return max(all_results, key=lambda x: x[1])
        elif strategy == "lowest":
            # Lowest Y-coordinate
            return min(all_results, key=lambda x: x[1])
        else:
            if self.debug:
                print(f"[DEBUG] Unknown strategy '{strategy}', using 'first'")
            return all_results[0]
    
    def is_text_present(self, pdf_path: Union[str, Path], search_string: str) -> bool:
        """
        Check if text is present anywhere in the document.
        
        Args:
            pdf_path: Path to the PDF file
            search_string: Text to search for
            
        Returns:
            True if text is found anywhere in the document, False otherwise
        """
        result = self.find_text_position(pdf_path, search_string)
        return result is not None
    
    def get_text_context(self, pdf_path: Union[str, Path], search_string: str, 
                        context_lines: int = 2) -> Optional[str]:
        """
        Get text context around the first occurrence of the search string.
        
        Args:
            pdf_path: Path to the PDF file
            search_string: Text to search for
            context_lines: Number of lines before/after to include
            
        Returns:
            Context text around the search string, None if not found
        """
        position = self.find_text_position(pdf_path, search_string)
        if not position:
            return None
        
        page_num, y_coord = position
        
        with PDFDocument(pdf_path) as doc:
            page = doc[page_num]
            text = page._page.get_text()
            
            # Simple context extraction (could be enhanced)
            lines = text.split('\n')
            target_line_index = None
            
            for i, line in enumerate(lines):
                if search_string in line:
                    target_line_index = i
                    break
            
            if target_line_index is not None:
                start_index = max(0, target_line_index - context_lines)
                end_index = min(len(lines), target_line_index + context_lines + 1)
                context_lines_list = lines[start_index:end_index]
                return '\n'.join(context_lines_list)
        
        return None