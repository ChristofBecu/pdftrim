"""
Application controller for PDF Trimmer.

This module provides the ApplicationController class that serves as the main
coordination point for the entire application, orchestrating the workflow
between CLI handling, processing, and output.
"""

import sys
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..ui.cli_handler import ParsedArguments

from ..di.interfaces import (
    IApplicationController, ICLIHandler, IDisplayManager, 
    IFileManager, IPDFProcessor, IConfig
)
from ..services.workflow_manager import WorkflowManager


class ApplicationController(IApplicationController):
    """
    Main application controller that coordinates all components.
    
    This class serves as the central coordination point for the PDF trimmer
    application, orchestrating the complete workflow from CLI argument parsing
    through PDF processing and output generation.
    """
    
    def __init__(self,
                 cli_handler: ICLIHandler,
                 display: IDisplayManager,
                 file_manager: IFileManager,
                 processor: IPDFProcessor,
                 config: IConfig):
        """
        Initialize the ApplicationController with injected dependencies.
        
        Args:
            cli_handler: Handler for command line interface operations
            display: Manager for output and display formatting
            file_manager: Manager for file operations
            processor: Processor for PDF operations
            config: Configuration management
        """
        self.cli_handler = cli_handler
        self.display = display
        self.file_manager = file_manager
        self.processor = processor
        self.config = config
        
        # Create workflow manager with injected dependencies
        self.workflow_manager = WorkflowManager(
            display=display,
            processor=processor,
            file_manager=file_manager,
            config=config,
            debug=config.debug_mode
        )
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the complete application workflow.
        
        This is the main entry point that coordinates:
        1. CLI argument parsing and validation
        2. Workflow execution (single file or batch)
        3. Error handling and exit code management
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            # Parse and validate command line arguments
            parsed_args = self._parse_arguments(args)
            if parsed_args is None:
                return 0  # Help/version was displayed, normal exit
            
            # Execute the appropriate workflow
            success = self._execute_workflow(parsed_args)
            
            # Return appropriate exit code
            return 0 if success else 1
            
        except KeyboardInterrupt:
            self.display.info("\nOperation cancelled by user.")
            return 130  # Standard exit code for Ctrl+C
            
        except Exception as e:
            self.display.error(f"Unexpected error: {e}")
            if self.config.debug_mode:
                import traceback
                self.display.error(f"Traceback: {traceback.format_exc()}")
            return 1
    
    def _parse_arguments(self, args: Optional[List[str]]) -> Optional['ParsedArguments']:
        """
        Parse command line arguments using the CLI handler.
        
        Args:
            args: Command line arguments
            
        Returns:
            Parsed arguments object, or None if help/version was shown
        """
        # Import the CLIResult type
        from .cli_handler import CLIResult
        
        # Use the new method that returns a result instead of calling sys.exit()
        result = self.cli_handler.handle_arguments_with_result(args)
        
        if result.should_exit:
            # For help/version (exit code 0), return None to indicate normal exit
            # For errors (exit code != 0), raise SystemExit to propagate the error
            if result.exit_code == 0:
                return None
            else:
                raise SystemExit(result.exit_code)
        
        return result.parsed_args
    
    def _execute_workflow(self, parsed_args) -> bool:
        """
        Execute the appropriate workflow based on parsed arguments.
        
        Args:
            parsed_args: Parsed command line arguments
            
        Returns:
            True if workflow completed successfully, False otherwise
        """
        try:
            # Extract workflow parameters
            input_path = getattr(parsed_args, 'input_path', None)
            search_string = getattr(parsed_args, 'search_string', '')
            output_dir = getattr(parsed_args, 'output_dir', None)
            is_batch_mode = getattr(parsed_args, 'is_batch_mode', False)
            
            # Validate required parameters
            if not search_string.strip():
                self.display.error("Search string cannot be empty")
                return False
            
            # Execute workflow
            success = self.workflow_manager.process_workflow(
                input_path=input_path if not is_batch_mode else None,
                search_string=search_string,
                output_dir=output_dir,
                is_batch_mode=is_batch_mode
            )
            
            return success
            
        except Exception as e:
            self.display.error(f"Workflow execution failed: {e}")
            if self.config.debug_mode:
                import traceback
                self.display.debug(f"Workflow error traceback: {traceback.format_exc()}")
            return False
    
    def get_application_info(self) -> dict:
        """
        Get information about the application state.
        
        Returns:
            Dictionary with application information
        """
        return {
            'debug_mode': self.config.debug_mode,
            'output_dir': self.config.output_dir,
            'output_suffix': self.config.output_suffix,
            'pdf_pattern': self.config.pdf_pattern,
            'workflow_stats': self.workflow_manager.get_processor_stats()
        }
    
    def validate_environment(self) -> bool:
        """
        Validate that the application environment is properly configured.
        
        Returns:
            True if environment is valid, False otherwise
        """
        try:
            # Check if output directory is accessible
            output_dir = self.config.output_dir
            self.file_manager.ensure_output_directory(output_dir)
            
            # Validate configuration
            if not self.config.output_suffix:
                self.display.warning("Output suffix is empty, files may be overwritten")
            
            if not self.config.pdf_pattern:
                self.display.error("PDF pattern is not configured")
                return False
            
            self.display.debug("Environment validation passed")
            return True
            
        except Exception as e:
            self.display.error(f"Environment validation failed: {e}")
            return False