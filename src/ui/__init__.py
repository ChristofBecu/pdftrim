"""
User interface components and presentation layer.

This module provides all user interaction components including command-line
interface handling, output formatting, and display management. The UI layer
is designed to be clean, informative, and support both interactive and
batch processing scenarios.

Key Components:
- CLIHandler: Command-line argument parsing and validation
- DisplayManager: Formatted output, logging, and user feedback
- Controllers: Application flow control and coordination

Features:
- Colored output support for better user experience
- Debug mode with verbose logging capabilities
- Progress indication for long-running operations
- Comprehensive error message formatting
- Flexible output configuration

The UI layer maintains clean separation from business logic and supports
easy extension for additional interface types (GUI, web, etc.) while
providing excellent user experience for command-line usage.
"""