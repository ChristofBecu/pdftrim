"""
DisplayManager - Centralized output and display formatting for PDF Trimmer.

This module provides consistent formatting and display management across the application,
separating presentation logic from business logic.
"""

import sys
from enum import Enum
from typing import Optional
from dataclasses import dataclass

from ..di.interfaces import IDisplayManager


class MessageType(Enum):
    """Types of messages that can be displayed."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class DisplayConfig:
    """Configuration for display formatting."""
    debug_enabled: bool = False
    use_colors: bool = True


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
    
