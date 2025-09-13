"""
DisplayManager - Centralized output and display formatting for PDF Trimmer.

This module provides consistent formatting and display management across the application,
separating presentation logic from business logic.
"""

import sys
from enum import Enum
from typing import List, Optional, Any
from dataclasses import dataclass

from ..di.interfaces import IDisplayManager


class MessageType(Enum):
    """Types of messages that can be displayed."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"


@dataclass
class DisplayConfig:
    """Configuration for display formatting."""
    debug_enabled: bool = False
    use_colors: bool = True
    separator_char: str = "-"
    separator_length: int = 50
    indent_size: int = 2


class DisplayManager(IDisplayManager):
    """
    Centralized display and output formatting manager.
    
    Handles all types of output including debug messages, progress reporting,
    error display, and status updates with consistent formatting.
    """
    
    def __init__(self, config: Optional[DisplayConfig] = None):
        """
        Initialize the DisplayManager.
        
        Args:
            config: Display configuration (uses defaults if None)
        """
        self.config = config or DisplayConfig()
        
    def debug(self, message: str, **kwargs) -> None:
        """
        Display a debug message.
        
        Args:
            message: Debug message to display
            **kwargs: Additional formatting options
        """
        if self.config.debug_enabled:
            formatted_msg = self._format_message(MessageType.DEBUG, message, **kwargs)
            print(formatted_msg)
    
    def info(self, message: str, **kwargs) -> None:
        """
        Display an informational message.
        
        Args:
            message: Info message to display
            **kwargs: Additional formatting options
        """
        formatted_msg = self._format_message(MessageType.INFO, message, **kwargs)
        print(formatted_msg)
    
    def success(self, message: str, **kwargs) -> None:
        """
        Display a success message.
        
        Args:
            message: Success message to display
            **kwargs: Additional formatting options
        """
        formatted_msg = self._format_message(MessageType.SUCCESS, message, **kwargs)
        print(formatted_msg)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Display a warning message.
        
        Args:
            message: Warning message to display
            **kwargs: Additional formatting options
        """
        formatted_msg = self._format_message(MessageType.WARNING, message, **kwargs)
        print(formatted_msg, file=sys.stderr)
    
    def error(self, message: str, **kwargs) -> None:
        """
        Display an error message.
        
        Args:
            message: Error message to display
            **kwargs: Additional formatting options
        """
        formatted_msg = self._format_message(MessageType.ERROR, message, **kwargs)
        print(formatted_msg, file=sys.stderr)
    
    def progress(self, message: str, **kwargs) -> None:
        """
        Display a progress message.
        
        Args:
            message: Progress message to display
            **kwargs: Additional formatting options
        """
        formatted_msg = self._format_message(MessageType.PROGRESS, message, **kwargs)
        print(formatted_msg)
    
    def separator(self, title: Optional[str] = None) -> None:
        """
        Display a separator line with optional title.
        
        Args:
            title: Optional title to include in separator
        """
        char = self.config.separator_char
        length = self.config.separator_length
        
        if title:
            # Center the title in the separator
            title_padded = f" {title} "
            if len(title_padded) >= length:
                print(title_padded)
            else:
                padding = (length - len(title_padded)) // 2
                line = char * padding + title_padded + char * (length - padding - len(title_padded))
                print(line)
        else:
            print(char * length)
    
    def blank_line(self, count: int = 1) -> None:
        """
        Display blank lines.
        
        Args:
            count: Number of blank lines to display
        """
        for _ in range(count):
            print()
    
    def list_items(self, items: List[str], title: Optional[str] = None, bullet: str = "  - ") -> None:
        """
        Display a list of items with consistent formatting.
        
        Args:
            items: List of items to display
            title: Optional title for the list
            bullet: Bullet character(s) to use
        """
        if title:
            self.info(title)
        
        for item in items:
            print(f"{bullet}{item}")
    
    def processing_start(self, count: int, operation: str, details: Optional[str] = None) -> None:
        """
        Display processing start message.
        
        Args:
            count: Number of items to process
            operation: Description of the operation
            details: Optional additional details
        """
        message = f"Processing {count} {operation}"
        if count == 1:
            # Remove plural 's' for single items
            if operation.endswith('s'):
                message = f"Processing {count} {operation[:-1]}"
        
        self.info(message)
        
        if details:
            self.info(details)
        
        self.separator()
    
    def processing_complete(self, successful: int, failed: int, operation: str = "item(s)") -> None:
        """
        Display processing completion summary.
        
        Args:
            successful: Number of successful operations
            failed: Number of failed operations
            operation: Description of what was processed
        """
        self.separator()
        message = f"Processing complete: {successful} successful, {failed} failed {operation}"
        
        if failed == 0:
            self.success(message)
        elif successful == 0:
            self.error(message)
        else:
            self.warning(message)
    
    def file_processing_result(self, filename: str, output_filename: str, status: str) -> None:
        """
        Display file processing result.
        
        Args:
            filename: Input filename
            output_filename: Output filename
            status: Processing status message
        """
        if "success" in status.lower() or "✓" in status:
            symbol = "✓"
        elif "error" in status.lower() or "✗" in status:
            symbol = "✗"
        else:
            symbol = "•"
        
        # Truncate long filenames for display
        display_input = self._truncate_filename(filename, 40)
        display_output = self._truncate_filename(output_filename, 40)
        
        message = f"{symbol} Processed: {display_input} -> {display_output} ({status})"
        print(message)
    
    def search_result(self, search_string: str, found: bool, page_num: Optional[int] = None, 
                      y_coord: Optional[float] = None) -> None:
        """
        Display search result information.
        
        Args:
            search_string: The string that was searched for
            found: Whether the string was found
            page_num: Page number where found (if applicable)
            y_coord: Y-coordinate where found (if applicable)
        """
        if found and page_num is not None:
            if y_coord is not None:
                self.debug(f"Found '{search_string}' on page {page_num} at Y-coordinate {y_coord}")
            else:
                self.debug(f"Found '{search_string}' on page {page_num}")
        else:
            self.debug(f"Text '{search_string}' not found in document")
    
    def operation_status(self, operation: str, details: str) -> None:
        """
        Display operation status with details.
        
        Args:
            operation: Operation description
            details: Status details
        """
        self.debug(f"{operation}: {details}")
    
    def _format_message(self, msg_type: MessageType, message: str, **kwargs) -> str:
        """
        Format a message according to its type.
        
        Args:
            msg_type: Type of message
            message: Message content
            **kwargs: Additional formatting options
            
        Returns:
            Formatted message string
        """
        # Add timestamp if requested
        timestamp = kwargs.get('timestamp', False)
        prefix = kwargs.get('prefix', '')
        suffix = kwargs.get('suffix', '')
        
        # Build the formatted message
        parts = []
        
        if prefix:
            parts.append(prefix)
        
        if msg_type == MessageType.DEBUG:
            parts.append(f"[DEBUG] {message}")
        elif msg_type == MessageType.SUCCESS:
            parts.append(f"✓ {message}")
        elif msg_type == MessageType.ERROR:
            parts.append(f"✗ {message}")
        elif msg_type == MessageType.WARNING:
            parts.append(f"⚠ {message}")
        else:
            parts.append(message)
        
        if suffix:
            parts.append(suffix)
        
        return " ".join(parts)
    
    def _truncate_filename(self, filename: str, max_length: int) -> str:
        """
        Truncate filename for display if too long.
        
        Args:
            filename: Filename to truncate
            max_length: Maximum length allowed
            
        Returns:
            Truncated filename with ellipsis if needed
        """
        if len(filename) <= max_length:
            return filename
        
        # Keep the extension and truncate the middle
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            available = max_length - len(ext) - 4  # 4 for "..." and "."
            if available > 0:
                return f"{name[:available]}...{ext}"
        
        # Fallback: truncate from end
        return f"{filename[:max_length-3]}..."