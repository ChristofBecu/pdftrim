"""
File service for PDF operations.

This module provides the FileService class for handling all file operations
including file discovery, path validation, output filename generation, and
directory management.
"""

import os
import glob
from typing import List, Optional, Union, Tuple
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
    
    def get_file_info(self, filepath: Union[str, Path]) -> dict:
        """
        Get comprehensive information about a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with file information
        """
        filepath = str(filepath)
        
        if not os.path.exists(filepath):
            return {'exists': False, 'error': 'File not found'}
        
        try:
            stat = os.stat(filepath)
            abs_path = os.path.abspath(filepath)
            
            return {
                'exists': True,
                'path': abs_path,
                'basename': os.path.basename(abs_path),
                'dirname': os.path.dirname(abs_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'is_pdf': abs_path.lower().endswith('.pdf'),
                'is_processed': self._is_processed_file(abs_path),
                'readable': os.access(abs_path, os.R_OK),
                'writable': os.access(abs_path, os.W_OK)
            }
        except OSError as e:
            return {'exists': True, 'error': f'Cannot access file: {e}'}
    
    def get_unique_output_filename(self, input_file: Union[str, Path], 
                                  output_dir: Optional[Union[str, Path]] = None) -> str:
        """
        Generate a unique output filename that doesn't conflict with existing files.
        
        Args:
            input_file: Path to input file
            output_dir: Output directory (defaults to config.output_dir)
            
        Returns:
            Full path to unique output file
        """
        base_output = self.create_output_filename(input_file, output_dir)
        
        if not os.path.exists(base_output):
            return base_output
        
        # File exists, create unique name
        directory = os.path.dirname(base_output)
        basename = os.path.basename(base_output)
        name, ext = os.path.splitext(basename)
        
        counter = 1
        while True:
            unique_name = f"{name}_{counter:03d}{ext}"
            unique_path = os.path.join(directory, unique_name)
            
            if not os.path.exists(unique_path):
                self.display.debug(f"Created unique output filename: {unique_path}")
                return unique_path
            
            counter += 1
            if counter > 999:  # Safety limit
                raise FileValidationError(f"Cannot create unique filename after 999 attempts for {base_output}")
    
    def cleanup_temp_files(self, directory: Union[str, Path], 
                          pattern: str = "*.tmp") -> int:
        """
        Clean up temporary files in a directory.
        
        Args:
            directory: Directory to clean
            pattern: File pattern to match (default: *.tmp)
            
        Returns:
            Number of files removed
        """
        directory = str(directory)
        temp_pattern = os.path.join(directory, pattern)
        temp_files = glob.glob(temp_pattern)
        
        removed_count = 0
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                removed_count += 1
                self.display.debug(f"Removed temp file: {temp_file}")
            except OSError as e:
                self.display.debug(f"Failed to remove temp file {temp_file}: {e}")
        
        return removed_count
    
    def get_directory_stats(self, directory: Union[str, Path]) -> dict:
        """
        Get statistics about PDFs in a directory.
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Dictionary with directory statistics
        """
        directory = str(directory)
        
        if not os.path.exists(directory):
            return {'error': 'Directory not found'}
        
        pdf_files = self.find_pdf_files(directory)
        processed_files = [f for f in glob.glob(os.path.join(directory, "*.pdf")) 
                          if self._is_processed_file(f)]
        
        total_size = 0
        for pdf_file in pdf_files:
            try:
                total_size += os.path.getsize(pdf_file)
            except OSError:
                pass
        
        return {
            'directory': os.path.abspath(directory),
            'total_pdfs': len(pdf_files) + len(processed_files),
            'unprocessed_pdfs': len(pdf_files),
            'processed_pdfs': len(processed_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': [os.path.basename(f) for f in pdf_files]
        }
    
    def batch_validate_files(self, filepaths: List[Union[str, Path]]) -> Tuple[List[str], List[str]]:
        """
        Validate multiple files in batch.
        
        Args:
            filepaths: List of file paths to validate
            
        Returns:
            Tuple of (valid_files, invalid_files_with_errors)
        """
        valid_files = []
        invalid_files = []
        
        for filepath in filepaths:
            try:
                valid_path = self.validate_input_file(filepath)
                valid_files.append(valid_path)
            except FileValidationError as e:
                invalid_files.append(f"{filepath}: {e}")
        
        self.display.debug(f"Batch validation: {len(valid_files)} valid, {len(invalid_files)} invalid")
        
        return valid_files, invalid_files