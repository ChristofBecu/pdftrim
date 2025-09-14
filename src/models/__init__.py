"""
PDF models and data structures.

This module defines the core data models used throughout the PDF trimming application.
These models provide enhanced wrappers around PyMuPDF objects and structured data
for processing results and configuration.

Key Models:
- PDFDocument: Enhanced wrapper around PyMuPDF documents with context management
- Page: Enhanced wrapper around PyMuPDF pages with utility methods
- ProcessingResult: Comprehensive result data from PDF processing operations
- ParsedArguments: Structured command-line argument representation

Features:
- Context manager support for proper resource cleanup
- Type-safe interfaces with comprehensive type hints
- Rich metadata capture for processing results
- Integration with dependency injection system

The models provide a clean abstraction layer over PyMuPDF while maintaining
performance and adding convenience methods for common operations like
blank page detection, text extraction, and document manipulation.
"""