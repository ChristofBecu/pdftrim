"""Configuration management for PDF trimmer application."""

import os
from typing import Optional


class Config:
    """Centralized configuration for PDF trimmer."""
    
    # Default values
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_OUTPUT_SUFFIX = "_edit"
    DEFAULT_PDF_PATTERN = "*.pdf"
    DEFAULT_PROCESSED_SUFFIX = "_edit.pdf"
    DEFAULT_DEBUG_MODE = False
    
    def __init__(self):
        """Initialize configuration with default values."""
        self._debug_mode = self._get_env_bool("PDF_TRIMMER_DEBUG", self.DEFAULT_DEBUG_MODE)
        self._output_dir = self._get_env_str("PDF_TRIMMER_OUTPUT_DIR", self.DEFAULT_OUTPUT_DIR)
        self._output_suffix = self._get_env_str("PDF_TRIMMER_OUTPUT_SUFFIX", self.DEFAULT_OUTPUT_SUFFIX)
        self._pdf_pattern = self._get_env_str("PDF_TRIMMER_PDF_PATTERN", self.DEFAULT_PDF_PATTERN)
        self._processed_suffix = self._get_env_str("PDF_TRIMMER_PROCESSED_SUFFIX", self.DEFAULT_PROCESSED_SUFFIX)
    
    @staticmethod
    def _get_env_bool(env_var: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(env_var)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def _get_env_str(env_var: str, default: str) -> str:
        """Get string value from environment variable."""
        return os.getenv(env_var, default)
    
    @property
    def debug_mode(self) -> bool:
        """Get debug mode setting."""
        return self._debug_mode
    
    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        """Set debug mode."""
        self._debug_mode = value
    
    @property
    def output_dir(self) -> str:
        """Get default output directory."""
        return self._output_dir
    
    @output_dir.setter
    def output_dir(self, value: str) -> None:
        """Set output directory."""
        self._output_dir = value
    
    @property
    def output_suffix(self) -> str:
        """Get output file suffix."""
        return self._output_suffix
    
    @output_suffix.setter
    def output_suffix(self, value: str) -> None:
        """Set output file suffix."""
        self._output_suffix = value
    
    @property
    def pdf_pattern(self) -> str:
        """Get PDF file search pattern."""
        return self._pdf_pattern
    
    @pdf_pattern.setter
    def pdf_pattern(self, value: str) -> None:
        """Set PDF file search pattern."""
        self._pdf_pattern = value
    
    @property
    def processed_suffix(self) -> str:
        """Get processed file suffix to skip."""
        return self._processed_suffix
    
    @processed_suffix.setter
    def processed_suffix(self, value: str) -> None:
        """Set processed file suffix."""
        self._processed_suffix = value
    
    def create_output_filename(self, input_file: str, output_dir: Optional[str] = None) -> str:
        """Generate output filename in the specified output directory."""
        output_directory = output_dir or self.output_dir
        filename = os.path.basename(input_file)
        base, ext = os.path.splitext(filename)
        return os.path.join(output_directory, f"{base}{self.output_suffix}{ext}")
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (f"Config(debug={self.debug_mode}, "
                f"output_dir='{self.output_dir}', "
                f"output_suffix='{self.output_suffix}')")


# Global config instance
config = Config()

# Global display manager instance
from ..ui.display_manager import DisplayManager
display = DisplayManager()