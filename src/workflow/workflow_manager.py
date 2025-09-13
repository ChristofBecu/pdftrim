"""
Workflow management for PDF processing operations.

This module provides the WorkflowManager class for orchestrating
PDF processing workflows, handling both single file and batch processing
with consistent error handling, progress reporting, and output management.
"""

from typing import Optional, List, Tuple
from pathlib import Path

from ..di.interfaces import IDisplayManager, IFileManager, IPDFProcessor, ICLIHandler, IConfig


class WorkflowManager:
    """
    Manages PDF processing workflows with centralized orchestration.
    
    This class eliminates duplication between single file and batch processing
    by providing consistent workflow orchestration, output directory handling,
    and progress reporting. Uses dependency injection for better testability.
    """
    
    def __init__(self, 
                 display: IDisplayManager,
                 processor: IPDFProcessor,
                 file_manager: IFileManager,
                 cli_handler: ICLIHandler,
                 config: IConfig,
                 debug: Optional[bool] = None):
        """
        Initialize the WorkflowManager with injected dependencies.
        
        Args:
            display: DisplayManager instance for output
            processor: PDFProcessor for handling PDF operations
            file_manager: FileManager for file operations
            cli_handler: CLIHandler for CLI interactions
            config: Configuration instance
            debug: Enable debug mode (uses config default if None)
        """
        self.display = display
        self.processor = processor
        self.file_manager = file_manager
        self.cli_handler = cli_handler
        self.config = config
        self.debug = debug if debug is not None else config.debug_mode
    
    def process_single_file(self, input_file: str, search_string: str, 
                           output_dir: Optional[str] = None) -> bool:
        """
        Process a single PDF file.
        
        Args:
            input_file: Path to the input PDF file
            search_string: Text to search for as the cutoff point
            output_dir: Directory to save the output file (uses config default if None)
            
        Returns:
            True if processing was successful, False otherwise
        """
        # Handle output directory defaulting
        resolved_output_dir = output_dir or self.config.output_dir
        
        # Display processing start
        self.cli_handler.display_processing_start(1, search_string, resolved_output_dir)
        
        # Process the PDF
        result = self.processor.process_pdf(input_file, search_string, resolved_output_dir)
        
        # Display result using CLI handler
        self.cli_handler.display_result(result)
        
        # Display completion status
        if result.success:
            self.cli_handler.display_processing_complete(1, 0)
        else:
            self.cli_handler.display_processing_complete(0, 1)
        
        return result.success
    
    def process_batch(self, search_string: str, output_dir: Optional[str] = None) -> Tuple[int, int]:
        """
        Process all PDF files in the current directory.
        
        Args:
            search_string: Text to search for as the cutoff point
            output_dir: Directory to save output files (uses config default if None)
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        # Handle output directory defaulting
        resolved_output_dir = output_dir or self.config.output_dir
        
        # Find PDF files using FileManager
        pdf_files = self.file_manager.find_pdf_files()
        
        # Check if any files were found
        if not pdf_files:
            self.cli_handler.display_no_files_found()
            return 0, 0
        
        # Display file list and processing start
        self.cli_handler.display_file_list(
            pdf_files, 
            f"Found {len(pdf_files)} PDF file(s) to process:"
        )
        self.cli_handler.display_processing_start(len(pdf_files), search_string, resolved_output_dir)
        
        # Process each file
        successful = 0
        failed = 0
        
        for pdf_file in pdf_files:
            result = self.processor.process_pdf(pdf_file, search_string, resolved_output_dir)
            
            if result.success:
                successful += 1
            else:
                failed += 1
                # Display individual file error
                self.display.error(f"Failed to process {pdf_file}: {result.message}")
        
        # Display completion status
        self.cli_handler.display_processing_complete(successful, failed)
        
        return successful, failed
    
    def process_workflow(self, input_path: Optional[str], search_string: str, 
                        output_dir: Optional[str] = None, is_batch_mode: bool = False) -> bool:
        """
        Process workflow based on input parameters.
        
        This is a high-level method that determines whether to use single file
        or batch processing based on the parameters.
        
        Args:
            input_path: Path to input file (None for batch mode)
            search_string: Text to search for as the cutoff point
            output_dir: Directory to save output files (uses config default if None)
            is_batch_mode: True for batch processing, False for single file
            
        Returns:
            True if all processing was successful, False if any failures occurred
        """
        if is_batch_mode or input_path is None:
            # Batch processing mode
            successful, failed = self.process_batch(search_string, output_dir)
            return failed == 0
        else:
            # Single file processing mode
            return self.process_single_file(input_path, search_string, output_dir)
    
    def get_processor_stats(self) -> dict:
        """
        Get processing statistics from the underlying PDFProcessor.
        
        Returns:
            Dictionary containing processing statistics
        """
        return {
            'files_processed': getattr(self.processor, '_files_processed', 0),
            'pages_removed': getattr(self.processor, '_pages_removed', 0),
            'blank_pages_removed': getattr(self.processor, '_blank_pages_removed', 0)
        }