"""
Dependency injection interfaces and protocols for PDF Trimmer.

This module defines the contracts/interfaces that enable dependency injection
and improve testability throughout the application.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Union, Any
from pathlib import Path


class IDisplayManager(ABC):
    """Interface for display/output management."""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Display a debug message."""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Display an informational message."""
        pass
    
    @abstractmethod
    def success(self, message: str, **kwargs) -> None:
        """Display a success message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Display a warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Display an error message."""
        pass


class IFileManager(ABC):
    """Interface for file management operations."""
    
    @abstractmethod
    def find_pdf_files(self, directory: Union[str, Path] = ".") -> List[str]:
        """Find all PDF files in the given directory."""
        pass
    
    @abstractmethod
    def validate_input_file(self, filepath: Union[str, Path]) -> str:
        """Validate that an input file exists and is accessible."""
        pass
    
    @abstractmethod
    def create_output_filename(self, input_file: Union[str, Path], 
                              output_dir: Optional[Union[str, Path]] = None) -> str:
        """Generate output filename in the specified output directory."""
        pass
    
    @abstractmethod
    def ensure_output_directory(self, output_dir: Union[str, Path]) -> str:
        """Create output directory if it doesn't exist."""
        pass


class ITextSearchEngine(ABC):
    """Interface for text search operations."""
    
    @abstractmethod
    def find_text_position(self, pdf_path: Union[str, Path], search_string: str) -> Optional[Tuple[int, float]]:
        """Find the first occurrence of text in a PDF document."""
        pass
    
    @abstractmethod
    def find_all_text_positions(self, pdf_path: Union[str, Path], search_string: str) -> List[Tuple[int, float]]:
        """Find all occurrences of text in a PDF document."""
        pass
    
    @abstractmethod
    def is_text_present(self, pdf_path: Union[str, Path], search_string: str) -> bool:
        """Check if text is present anywhere in the document."""
        pass


class IPDFProcessor(ABC):
    """Interface for PDF processing operations."""
    
    @abstractmethod
    def process_pdf(self, input_file: Union[str, Path], search_string: str, 
                   output_dir: Union[str, Path]) -> Any:
        """Process a PDF file with trimming based on search string."""
        pass
    
    @abstractmethod
    def batch_process(self, input_files: List[Union[str, Path]], search_string: str, 
                     output_dir: Union[str, Path]) -> List:
        """Process multiple PDF files in batch."""
        pass


class ICLIHandler(ABC):
    """Interface for command line interface operations."""
    
    @abstractmethod
    def handle_arguments(self, args: Optional[List[str]] = None) -> Any:
        """Parse arguments and handle special cases."""
        pass
    
    @abstractmethod
    def display_usage(self) -> None:
        """Display usage information to the user."""
        pass
    
    @abstractmethod
    def display_help(self) -> None:
        """Display comprehensive help information."""
        pass
    
    @abstractmethod
    def display_processing_start(self, count: int, search_string: str, output_dir: str) -> None:
        """Display processing start information."""
        pass
    
    @abstractmethod
    def display_processing_complete(self, successful: int, failed: int) -> None:
        """Display processing completion summary."""
        pass
    
    @abstractmethod
    def display_result(self, result) -> None:
        """Display a processing result."""
        pass
    
    @abstractmethod
    def display_no_files_found(self, file_type: str = "PDF files") -> None:
        """Display a message when no files are found."""
        pass
    
    @abstractmethod
    def display_file_list(self, files: List[str], title: str = "Files to process:") -> None:
        """Display a list of files."""
        pass


class IConfig(ABC):
    """Interface for configuration management."""
    
    @property
    @abstractmethod
    def debug_mode(self) -> bool:
        """Get debug mode setting."""
        pass
    
    @property
    @abstractmethod
    def output_dir(self) -> str:
        """Get default output directory."""
        pass
    
    @property
    @abstractmethod
    def output_suffix(self) -> str:
        """Get output file suffix."""
        pass
    
    @property
    @abstractmethod
    def pdf_pattern(self) -> str:
        """Get PDF file search pattern."""
        pass


class IApplicationController(ABC):
    """Interface for the main application controller."""
    
    @abstractmethod
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the complete application workflow.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        pass