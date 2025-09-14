"""
Configuration management for PDF trimmer.

This module provides centralized configuration management with environment variable
support and sensible defaults. The Config class handles all application settings
including output directories, file patterns, and debug modes.

Key Features:
- Environment variable support with PDF_TRIMMER_ prefix
- Read-only properties for critical settings
- Settable debug mode for runtime configuration
- Validation of configuration values

Usage:
    from src.config.settings import config
    
    # Use global configuration instance
    output_dir = config.output_dir
    config.debug_mode = True
    
    # Access environment-based settings
    pattern = config.pdf_pattern
    suffix = config.output_suffix
"""