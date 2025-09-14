"""
Core business logic for PDF processing.

This module contains the fundamental components for PDF trimming operations:
- PDFProcessor: Main processing logic for trimming PDFs from search text
- TextSearchEngine: Locates text within PDF documents

The core module handles the essential PDF manipulation operations including:
- Opening and parsing PDF documents
- Searching for specific text within pages
- Determining optimal trim points
- Creating trimmed output documents
- Performance optimization for large documents

Components:
- PDFProcessor: Orchestrates the complete trimming workflow
- TextSearchEngine: Efficient text location using PyMuPDF search capabilities

Both components support debug mode for detailed operation logging and
integrate with the dependency injection system for clean separation of concerns.
"""