"""Configuration management for PDF trimmer application."""

import os

from ..di.interfaces import IConfig


class Config(IConfig):
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
    
    @property
    def output_suffix(self) -> str:
        """Get output file suffix."""
        return self._output_suffix
    
    @property
    def pdf_pattern(self) -> str:
        """Get PDF file search pattern."""
        return self._pdf_pattern
    
    @property
    def processed_suffix(self) -> str:
        """Get processed file suffix to skip."""
        return self._processed_suffix
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (f"Config(debug={self.debug_mode}, "
                f"output_dir='{self.output_dir}', "
                f"output_suffix='{self.output_suffix}')")


# Global config instance
config = Config()