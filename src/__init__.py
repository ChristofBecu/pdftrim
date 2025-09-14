"""
PDF Trimmer - A modular tool for trimming PDF documents from a specific text search.

This package provides a clean architecture for PDF processing with dependency injection,
comprehensive error handling, and configurable logging. The system uses PyMuPDF for
PDF operations and supports both single file and batch processing workflows.

Architecture:
- `core`: Core PDF processing and text search functionality
- `models`: Data models for PDF documents, pages, and processing results
- `services`: Business logic for file management and workflow orchestration
- `ui`: Command-line interface and display management
- `di`: Dependency injection container and interfaces
- `config`: Configuration management with environment variable support

Key Components:
- PDFProcessor: Main PDF trimming logic
- TextSearchEngine: Text location within PDF documents
- FileService: File operations and validation
- WorkflowManager: Orchestrates complete processing workflows
- DisplayManager: Formatted output and logging

Usage:
    from src.di.container import create_container_with_debug
    from src.di.interfaces import IApplicationController
    
    container = create_container_with_debug(debug_enabled=False)
    controller = container.resolve(IApplicationController)
    exit_code = controller.run(sys.argv[1:])
"""