"""
File service for PDF operations.

This module provides the FileService class for handling all file operations
including file discovery, path validation, output filename generation, and
directory management.
"""

import os
import glob
from typing import List, Optional, Union
from pathlib import Path

from ..config.settings import config
from ..ui.display import DisplayManager, DisplayConfig
from ..di.interfaces import IFileManager


class FileValidationError(Exception):
    """Raised when file validation fails."""
    pass


class FileService(IFileManager):
    """
    A service for managing all file operations in the PDF trimmer.
    
    This service handles file discovery, validation, path generation, and
    directory management operations.
    """
    
    def __init__(self, debug: Optional[bool] = None, display_manager: Optional[DisplayManager] = None):
        """
        Initialize the FileManager.
        
        Args:
            debug: Enable debug logging (defaults to config.debug_mode if None)
            display_manager: Optional DisplayManager for output formatting
        """
        self.debug = debug if debug is not None else config.debug_mode
        
        # Use provided DisplayManager or create a default one
        if display_manager:
            self.display = display_manager
        else:
            display_config = DisplayConfig(debug_enabled=self.debug)
            self.display = DisplayManager(display_config)
    
    def find_pdf_files(self, directory: Union[str, Path] = ".") -> List[str]:
        """
        Find all PDF files in the given directory, excluding already processed files.
        
        Args:
            directory: Directory to search for PDF files
            
        Returns:
            List of PDF file paths
        """
        directory = str(directory)
        pdf_pattern = os.path.join(directory, config.pdf_pattern)
        
        self.display.debug(f"Searching for PDFs with pattern: {pdf_pattern}")
        
        pdf_files = glob.glob(pdf_pattern)
        
        # Filter out already processed files
        filtered_files = [f for f in pdf_files if not self._is_processed_file(f)]
        
        self.display.debug(f"Found {len(pdf_files)} total PDF files, {len(filtered_files)} unprocessed")
        if len(pdf_files) > len(filtered_files):
            skipped = len(pdf_files) - len(filtered_files)
            self.display.debug(f"Skipped {skipped} already processed files")
        
        return filtered_files
    
    def _is_processed_file(self, filepath: str) -> bool:
        """
        Check if a file appears to be already processed.
        
        Args:
            filepath: Path to the file to check
            
        Returns:
            True if the file appears to be already processed
        """
        return filepath.endswith(config.processed_suffix)
    
    def validate_input_file(self, filepath: Union[str, Path]) -> str:
        """
        Validate that an input file exists and is accessible.
        
        Args:
            filepath: Path to the input file
            
        Returns:
            Absolute path to the validated file
            
        Raises:
            FileValidationError: If file validation fails
        """
        filepath = str(filepath)
        
        if not os.path.exists(filepath):
            raise FileValidationError(f"File not found: {filepath}")
        
        if not os.path.isfile(filepath):
            raise FileValidationError(f"Path is not a file: {filepath}")
        
        if not os.access(filepath, os.R_OK):
            raise FileValidationError(f"File is not readable: {filepath}")
        
        # Check if it's a PDF file
        if not filepath.lower().endswith('.pdf'):
            raise FileValidationError(f"File is not a PDF: {filepath}")
        
        abs_path = os.path.abspath(filepath)
        
        self.display.debug(f"Validated input file: {abs_path}")
        
        return abs_path
    
    def create_output_filename(self, input_file: Union[str, Path], 
                              output_dir: Optional[Union[str, Path]] = None) -> str:
        """
        Generate output filename in the specified output directory.
        
        Args:
            input_file: Path to input file
            output_dir: Output directory (defaults to config.output_dir)
            
        Returns:
            Full path to output file
        """
        input_file = str(input_file)
        output_directory = str(output_dir) if output_dir else config.output_dir
        
        filename = os.path.basename(input_file)
        base, ext = os.path.splitext(filename)
        output_filename = f"{base}{config.output_suffix}{ext}"
        output_path = os.path.join(output_directory, output_filename)
        
        self.display.debug(f"Generated output filename: {output_path}")
        
        return output_path
    
    def ensure_output_directory(self, output_dir: Union[str, Path]) -> str:
        """
        Create output directory if it doesn't exist.
        
        Args:
            output_dir: Directory path to create
            
        Returns:
            Absolute path to the created/existing directory
            
        Raises:
            FileValidationError: If directory cannot be created
        """
        output_dir = str(output_dir)
        abs_output_dir = os.path.abspath(output_dir)
        
        try:
            if not os.path.exists(abs_output_dir):
                os.makedirs(abs_output_dir)
                self.display.debug(f"Created output directory: {abs_output_dir}")
            else:
                self.display.debug(f"Output directory already exists: {abs_output_dir}")
            
            # Verify directory is writable
            if not os.access(abs_output_dir, os.W_OK):
                raise FileValidationError(f"Output directory is not writable: {abs_output_dir}")
            
            return abs_output_dir
            
        except OSError as e:
            raise FileValidationError(f"Cannot create output directory {abs_output_dir}: {e}")