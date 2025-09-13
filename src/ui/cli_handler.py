"""
Command line interface handler for the PDF trimmer.

This module provides the CLIHandler class for handling command line argument
parsing, validation, and user interface messaging.
"""

import sys
from typing import Optional, List
from dataclasses import dataclass

from ..config.settings import config
from .display import DisplayManager
from ..di.interfaces import ICLIHandler


class CLIError(Exception):
    """Raised when command line interface encounters an error."""
    pass


@dataclass
class ParsedArguments:
    """Container for parsed command line arguments."""
    input_path: str
    search_string: str
    is_batch_mode: bool
    output_dir: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not self.search_string.strip():
            raise CLIError("Search string cannot be empty")


class CLIHandler(ICLIHandler):
    """
    A class for handling command line interface operations.
    
    This class handles argument parsing, validation, help messages,
    and user interface interactions for the PDF trimmer.
    """
    
    # Application metadata
    APP_NAME = "PDF Trimmer"
    APP_DESCRIPTION = "Removes pages from a PDF starting at a specific search string."
    VERSION = "2.0.0"
    
    # Usage messages
    USAGE_HEADER = "Usage:"
    USAGE_BATCH = "  python pdftrim.py 'search_string'                    # Process all PDFs in current directory"
    USAGE_SINGLE = "  python pdftrim.py input.pdf 'search_string'          # Process single PDF"
    USAGE_OUTPUT = "  Output files will be saved in 'output' directory"
    
    # Error messages
    ERROR_INVALID_ARGS = "Invalid number of arguments"
    ERROR_EMPTY_SEARCH = "Search string cannot be empty"
    ERROR_FILE_REQUIRED = "Input file path is required"
    
    def __init__(self, debug: Optional[bool] = None, display: Optional[DisplayManager] = None):
        """
        Initialize the CLIHandler.
        
        Args:
            debug: Enable debug logging (defaults to config.debug_mode if None)
            display: DisplayManager instance for output
        """
        self.debug = debug if debug is not None else config.debug_mode
        self.display = display or DisplayManager()
    
    def parse_arguments(self, args: Optional[List[str]] = None) -> ParsedArguments:
        """
        Parse and validate command line arguments.
        
        Args:
            args: List of arguments to parse (defaults to sys.argv[1:])
            
        Returns:
            ParsedArguments object with parsed data
            
        Raises:
            CLIError: If arguments are invalid
        """
        if args is None:
            args = sys.argv[1:]
        
        if self.debug:
            self.display.debug(f"Parsing arguments: {args}")
        
        # Validate argument count
        if len(args) not in [1, 2]:
            raise CLIError(f"{self.ERROR_INVALID_ARGS}. Expected 1 or 2 arguments, got {len(args)}")
        
        try:
            if len(args) == 1:
                # Batch mode: process all PDFs in current directory
                search_string = args[0]
                return ParsedArguments(
                    input_path=".",
                    search_string=search_string,
                    is_batch_mode=True
                )
            else:
                # Single file mode: process specific PDF
                input_path = args[0]
                search_string = args[1]
                return ParsedArguments(
                    input_path=input_path,
                    search_string=search_string,
                    is_batch_mode=False
                )
        except Exception as e:
            raise CLIError(f"Error parsing arguments: {e}")
    
    def display_usage(self) -> None:
        """Display usage information to the user."""
        print(self.USAGE_HEADER)
        print(self.USAGE_BATCH)
        print(self.USAGE_SINGLE)
        print(self.USAGE_OUTPUT)
    
    def display_help(self) -> None:
        """Display comprehensive help information."""
        print(f"{self.APP_NAME} v{self.VERSION}")
        print(f"{self.APP_DESCRIPTION}")
        print()
        self.display_usage()
        print()
        print("Arguments:")
        print("  search_string    Text to search for as the cutoff point")
        print("  input.pdf       (Optional) Specific PDF file to process")
        print()
        print("Behavior:")
        print("  - If only search_string is provided, all PDFs in current directory are processed")
        print("  - If input.pdf is provided, only that specific file is processed")
        print("  - Pages after the search string location are removed")
        print("  - Blank pages are automatically detected and removed")
        print("  - Processed files are saved with '_edit' suffix")
        print()
        print("Examples:")
        print("  python pdftrim.py 'Chapter 5'")
        print("  python pdftrim.py document.pdf 'Appendix A'")
        print()
        print("Environment Variables:")
        print(f"  PDF_TRIMMER_DEBUG=true          Enable debug output")
        print(f"  PDF_TRIMMER_OUTPUT_DIR=path     Set output directory (default: {config.output_dir})")
        print(f"  PDF_TRIMMER_OUTPUT_SUFFIX=str   Set output suffix (default: {config.output_suffix})")
    
    def display_version(self) -> None:
        """Display version information."""
        print(f"{self.APP_NAME} v{self.VERSION}")
    
    def handle_arguments(self, args: Optional[List[str]] = None) -> ParsedArguments:
        """
        Parse arguments and handle special cases (help, version, etc.).
        
        Args:
            args: List of arguments to parse (defaults to sys.argv[1:])
            
        Returns:
            ParsedArguments object
            
        Raises:
            SystemExit: If help/version is requested or arguments are invalid
        """
        if args is None:
            args = sys.argv[1:]
        
        # Handle special arguments first, regardless of other arguments
        if not args or any(arg in ['-h', '--help', 'help'] for arg in args):
            self.display_help()
            sys.exit(0)
        
        if any(arg in ['-v', '--version', 'version'] for arg in args):
            self.display_version()
            sys.exit(0)
        
        try:
            parsed_args = self.parse_arguments(args)
            
            if self.debug:
                print(f"[DEBUG] Parsed arguments: {parsed_args}")
            
            return parsed_args
            
        except CLIError as e:
            self.display_error(str(e))
            self.display_usage()
            sys.exit(1)
    
    def display_error(self, message: str) -> None:
        """
        Display an error message to the user.
        
        Args:
            message: Error message to display
        """
        self.display.error(message)
    
    def display_no_files_found(self, file_type: str = "PDF files") -> None:
        """
        Display a message when no files are found.
        
        Args:
            file_type: Type of files that were not found
        """
        print(f"No {file_type} found in current directory.")
    
    def display_result(self, result) -> None:
        """
        Display a processing result.
        
        Args:
            result: Result object to display
        """
        print(result)
    
    def display_info(self, message: str) -> None:
        """
        Display an informational message to the user.
        
        Args:
            message: Information message to display
        """
        print(message)
    
    def display_debug(self, message: str) -> None:
        """
        Display a debug message if debug mode is enabled.
        
        Args:
            message: Debug message to display
        """
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def confirm_action(self, message: str, default: bool = True) -> bool:
        """
        Ask user for confirmation.
        
        Args:
            message: Confirmation prompt message
            default: Default response if user just presses Enter
            
        Returns:
            True if user confirms, False otherwise
        """
        prompt_suffix = " [Y/n]" if default else " [y/N]"
        response = input(f"{message}{prompt_suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
    
    def display_processing_start(self, file_count: int, search_string: str, output_dir: str) -> None:
        """
        Display processing start information.
        
        Args:
            file_count: Number of files to process
            search_string: Search string being used
            output_dir: Output directory path
        """
        if file_count == 1:
            print(f"Processing 1 PDF file")
        else:
            print(f"Processing {file_count} PDF files")
        
        print(f"Search string: '{search_string}'")
        print(f"Output directory: {output_dir}")
        print("-" * 50)
    
    def display_processing_complete(self, successful: int, failed: int) -> None:
        """
        Display processing completion summary.
        
        Args:
            successful: Number of successfully processed files
            failed: Number of failed files
        """
        print("-" * 50)
        print(f"Processing complete: {successful} successful, {failed} failed")
    
    def display_file_list(self, files: List[str], title: str = "Files to process:") -> None:
        """
        Display a list of files.
        
        Args:
            files: List of file paths
            title: Title for the file list
        """
        import os
        
        print(f"{title}")
        for file_path in files:
            print(f"  - {os.path.basename(file_path)}")
    
    def get_user_input(self, prompt: str, validate_func=None) -> str:
        """
        Get user input with optional validation.
        
        Args:
            prompt: Prompt message to display
            validate_func: Optional function to validate input
            
        Returns:
            Validated user input
        """
        while True:
            user_input = input(f"{prompt}: ").strip()
            
            if validate_func:
                try:
                    if validate_func(user_input):
                        return user_input
                    else:
                        self.display.warning("Invalid input. Please try again.")
                except Exception as e:
                    self.display.error(f"Validation error: {e}")
            else:
                return user_input
    
    def validate_search_string(self, search_string: str) -> bool:
        """
        Validate search string input.
        
        Args:
            search_string: Search string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not search_string or not search_string.strip():
            print("Search string cannot be empty.")
            return False
        
        if len(search_string.strip()) < 2:
            print("Search string must be at least 2 characters long.")
            return False
        
        return True