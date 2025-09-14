"""
High-level services and orchestration.

This module contains business logic services that orchestrate complex workflows
and manage file operations. Services coordinate between core components to
provide complete application functionality.

Key Services:
- FileService: Comprehensive file operations, validation, and path management
- WorkflowManager: Orchestrates complete PDF processing workflows

Responsibilities:
- File system operations and validation
- Input/output path generation and management
- Workflow coordination between core components
- Error handling and recovery strategies
- Batch processing logic for multiple files

The services layer provides the business logic that coordinates between
the core processing components and the user interface, handling complex
workflows like batch processing and ensuring proper error handling
throughout the application lifecycle.
"""