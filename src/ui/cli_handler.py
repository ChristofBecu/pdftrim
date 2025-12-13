"""
Command line interface handler for the PDF trimmer.

This module provides the CLIHandler class for handling command line argument
parsing, validation, and user interface messaging.
"""

import sys
import argparse
from typing import Optional, List
from dataclasses import dataclass

from ..config.settings import config
from .display import DisplayManager
from ..di.interfaces import ICLIHandler


class CLIError(Exception):
    """Raised when command line interface encounters an error."""
    pass


class _ArgumentParserExit(Exception):
    """Internal exception used to prevent argparse from calling sys.exit()."""

    def __init__(self, status: int = 0):
        super().__init__(status)
        self.status = status


class _NoExitArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that raises instead of exiting the interpreter."""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise CLIError(message)

    def exit(self, status: int = 0, message: Optional[str] = None) -> None:  # type: ignore[override]
        if message:
            # argparse already formats the message with trailing newline
            print(message, end="")
        raise _ArgumentParserExit(status)


@dataclass
class ParsedArguments:
    """Container for parsed command line arguments."""
    input_path: str
    is_batch_mode: bool
    operation: str
    search_string: str = ""
    delete_spec: Optional[str] = None
    before_page: Optional[int] = None
    after_page: Optional[int] = None
    output_dir: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validation."""
        op = (self.operation or "").strip().lower()

        if op == "search":
            if not self.search_string.strip():
                raise CLIError("Search string cannot be empty")
        elif op == "delete":
            if not (self.delete_spec or "").strip():
                raise CLIError("Delete specification cannot be empty")
        elif op == "before_after":
            if self.before_page is None and self.after_page is None:
                raise CLIError("At least one of --before or --after must be provided")
            for flag, value in (("--before", self.before_page), ("--after", self.after_page)):
                if value is not None and value < 1:
                    raise CLIError(f"{flag} must be a positive, 1-based page number")
        else:
            raise CLIError("Invalid operation")


@dataclass
class CLIResult:
    """Result of CLI argument handling."""
    should_exit: bool = False
    exit_code: int = 0
    parsed_args: Optional[ParsedArguments] = None
    
    @classmethod
    def exit_with_code(cls, code: int) -> 'CLIResult':
        """Create a result that indicates the application should exit with the given code."""
        return cls(should_exit=True, exit_code=code)
    
    @classmethod
    def success_with_args(cls, args: ParsedArguments) -> 'CLIResult':
        """Create a result with successfully parsed arguments."""
        return cls(should_exit=False, exit_code=0, parsed_args=args)


class CLIHandler(ICLIHandler):
    """
    A class for handling command line interface operations.
    
    This class handles argument parsing, validation, help messages,
    and user interface interactions for the PDF trimmer.
    """
    
    # Application metadata
    APP_NAME = "PDF Trimmer"
    APP_DESCRIPTION = "Removes pages from a PDF starting at a specific search string."
    VERSION = "2.1.0"
    
    # Error messages
    ERROR_EMPTY_SEARCH = "Search string cannot be empty"
    
    def __init__(self, debug: Optional[bool] = None, display: Optional[DisplayManager] = None):
        """
        Initialize the CLIHandler.
        
        Args:
            debug: Enable debug logging (defaults to config.debug_mode if None)
            display: DisplayManager instance for output
        """
        self.debug = debug if debug is not None else config.debug_mode
        self.display = display or DisplayManager()

        self._parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = _NoExitArgumentParser(
            prog="pdftrim.py",
            description=self.APP_DESCRIPTION,
            add_help=True,
        )

        parser.add_argument(
            "-f",
            "--file",
            dest="file",
            help="Input PDF file path. If omitted, all PDFs in current directory are processed.",
        )

        parser.add_argument(
            "-s",
            "--search",
            dest="search",
            help="Trim from the first occurrence of this search string.",
        )

        parser.add_argument(
            "-d",
            "--delete",
            dest="delete",
            help="Delete specific pages/ranges (e.g. 1-4,7).",
        )

        parser.add_argument(
            "-b",
            "--before",
            dest="before",
            type=int,
            help="Delete pages before this page number (e.g. 10 deletes pages 1-9).",
        )

        parser.add_argument(
            "-a",
            "--after",
            dest="after",
            type=int,
            help="Delete pages after this page number (e.g. 10 deletes pages 11-end).",
        )

        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"{self.APP_NAME} v{self.VERSION}",
            help="Show version information and exit.",
        )

        return parser
    
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

        try:
            namespace = self._parser.parse_args(args)
        except _ArgumentParserExit as e:
            # Help/version already printed by argparse; map to CLIResult upstream.
            raise
        except CLIError:
            raise
        except Exception as e:
            raise CLIError(f"Error parsing arguments: {e}")

        # Validate operation combinations:
        # - Only --before and --after can be combined.
        # - --search is exclusive with everything else.
        # - --delete is exclusive with everything else.
        # Treat flag presence as selecting an operation, even if the value is
        # empty/whitespace. This allows us to emit specific validation errors
        # (e.g. "Search string cannot be empty") instead of "no operation".
        has_search = namespace.search is not None
        has_delete = namespace.delete is not None
        has_before = namespace.before is not None
        has_after = namespace.after is not None

        if has_search and (has_delete or has_before or has_after):
            raise CLIError("--search cannot be combined with --delete/--before/--after")
        if has_delete and (has_search or has_before or has_after):
            raise CLIError("--delete cannot be combined with --search/--before/--after")

        if not (has_search or has_delete or has_before or has_after):
            raise CLIError("You must specify one operation: --search, --delete, --before, or --after")

        if has_search:
            operation = "search"
        elif has_delete:
            operation = "delete"
        else:
            operation = "before_after"

        # Batch mode behavior: if -f/--file is omitted, process current directory.
        if namespace.file:
            input_path = namespace.file
            is_batch_mode = False
        else:
            input_path = "."
            is_batch_mode = True

        return ParsedArguments(
            input_path=input_path,
            is_batch_mode=is_batch_mode,
            operation=operation,
            search_string=namespace.search or "",
            delete_spec=namespace.delete,
            before_page=namespace.before,
            after_page=namespace.after,
        )
    
    def display_usage(self) -> None:
        """Display usage information to the user."""
        self._parser.print_usage()
    
    def display_help(self) -> None:
        """Display comprehensive help information."""
        self._parser.print_help()
        print()
        print("Environment Variables:")
        print("  PDF_TRIMMER_DEBUG=true          Enable debug output")
        print(f"  PDF_TRIMMER_OUTPUT_DIR=path     Set output directory (default: {config.output_dir})")
        print(f"  PDF_TRIMMER_OUTPUT_SUFFIX=str   Set output suffix (default: {config.output_suffix})")
    
    def display_version(self) -> None:
        """Display version information."""
        print(f"{self.APP_NAME} v{self.VERSION}")
    
    def handle_arguments_with_result(self, args: Optional[List[str]] = None) -> CLIResult:
        """
        Parse arguments and handle special cases, returning a result instead of exiting.
        
        Args:
            args: List of arguments to parse (defaults to sys.argv[1:])
            
        Returns:
            CLIResult indicating whether to exit and with what code, or parsed arguments
        """
        if args is None:
            args = sys.argv[1:]

        try:
            parsed_args = self.parse_arguments(args)
            if self.debug:
                print(f"[DEBUG] Parsed arguments: {parsed_args}")
            return CLIResult.success_with_args(parsed_args)
        except _ArgumentParserExit as e:
            # Help/version printed by argparse.
            return CLIResult.exit_with_code(e.status)
        except CLIError as e:
            self.display_error(str(e))
            self.display_usage()
            return CLIResult.exit_with_code(1)

    def handle_arguments(self, args: Optional[List[str]] = None) -> ParsedArguments:
        """
        Parse arguments and handle special cases (help, version, etc.).
        
        DEPRECATED: This method still calls sys.exit() for backward compatibility.
        Use handle_arguments_with_result() for better testability.
        
        Args:
            args: List of arguments to parse (defaults to sys.argv[1:])
            
        Returns:
            ParsedArguments object
            
        Raises:
            SystemExit: If help/version is requested or arguments are invalid
        """
        result = self.handle_arguments_with_result(args)
        
        if result.should_exit:
            sys.exit(result.exit_code)
        
        if result.parsed_args is None:
            # This shouldn't happen, but handle it gracefully
            sys.exit(1)
            
        return result.parsed_args
    
    def display_error(self, message: str) -> None:
        """
        Display an error message to the user.
        
        Args:
            message: Error message to display
        """
        self.display.error(message)
    
    

    

    

    

    

    

    

    

    
