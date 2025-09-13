"""
Result objects for PDF processing operations.

This module provides result classes that contain information about processing
outcomes including success status, output paths, and operation details.
"""

import os
from typing import Optional


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