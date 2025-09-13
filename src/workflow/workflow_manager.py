"""
Workflow management for PDF processing operations.

This module provides the WorkflowManager class for orchestrating
PDF processing workflows, handling both single file and batch processing
with consistent error handling, progress reporting, and output management.
"""

from typing import Optional, List, Tuple
from pathlib import Path

from ..di.interfaces import IDisplayManager, IFileManager, IPDFProcessor, IConfig


class WorkflowManager:
    """
    Manages PDF processing workflows with centralized orchestration.
    
    This class eliminates duplication between single file and batch processing
    by providing consistent workflow orchestration, output directory handling,
    and progress reporting. Focuses purely on workflow coordination without
    CLI-specific concerns.
    """
    
    def __init__(self, 
                 display: IDisplayManager,
                 processor: IPDFProcessor,
                 file_manager: IFileManager,
                 config: IConfig,
                 debug: Optional[bool] = None):
        """
        Initialize the WorkflowManager with injected dependencies.
        
        Args:
            display: DisplayManager instance for output
            processor: PDFProcessor for handling PDF operations
            file_manager: FileManager for file operations
            config: Configuration instance
            debug: Enable debug mode (uses config default if None)
        """
        self.display = display
        self.processor = processor
        self.file_manager = file_manager
        self.config = config
        self.debug = debug if debug is not None else config.debug_mode
    
    def process_single_file(self, input_file: str, search_string: str, output_dir: str = "") -> bool:
        """
        Process a single PDF file.
        
        Args:
            input_file: Path to the PDF file to process
            search_string: String to search for in the PDF
            output_dir: Output directory for processed file
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        resolved_output_dir = self.file_manager.ensure_output_directory(output_dir or self.config.output_dir)
        
        # Show processing start
        self.display.info(f"Processing file: {input_file}")
        self.display.info(f"Search string: '{search_string}'")
        self.display.info(f"Output directory: {resolved_output_dir}")
        
        # Process the file
        result = self.processor.process_pdf(input_file, search_string, resolved_output_dir)
        
        # Show result
        self.display.info(f"Result: {result.message}")
        if result.success:
            self.display.info(f"Output: {result.output_file}")
        
        if result.success:
            self.display.success("Processing complete: 1 successful, 0 failed")
            return True
        else:
            self.display.error("Processing complete: 0 successful, 1 failed")
            return False
    
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
        resolved_output_dir = self.file_manager.ensure_output_directory(resolved_output_dir)
        
        # Find PDF files using FileManager
        pdf_files = self.file_manager.find_pdf_files()
        
        # Check if any files were found
        if not pdf_files:
            self.display.info("No PDF files found in current directory.")
            return 0, 0
        
        # Display file list and processing start
        self.display.info(f"Found {len(pdf_files)} PDF file(s) to process:")
        for pdf_file in pdf_files:
            import os
            self.display.info(f"  - {os.path.basename(pdf_file)}")
        
        self.display.info(f"Processing {len(pdf_files)} PDF files")
        self.display.info(f"Search string: '{search_string}'")
        self.display.info(f"Output directory: {resolved_output_dir}")
        self.display.info("-" * 50)
        
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
        self.display.info("-" * 50)
        message = f"Processing complete: {successful} successful, {failed} failed"
        if failed == 0:
            self.display.success(message)
        elif successful == 0:
            self.display.error(message)
        else:
            self.display.warning(message)
        
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
            return self.process_single_file(input_path, search_string, output_dir or "")
    
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