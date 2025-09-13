#!/usr/bin/env python3
"""
PDF Trimmer - Removes pages from a PDF starting at a specific search string.
"""

# Import our custom classes
from src.cli.cli_handler import CLIHandler
from src.config.settings import config
from src.workflow.workflow_manager import WorkflowManager
from src.ui.display_manager import DisplayManager, DisplayConfig

# Initialize a global DisplayManager for functions that need debug output
display = DisplayManager(DisplayConfig(debug_enabled=config.debug_mode))


def main() -> None:
    """Main entry point."""
    # Initialize CLI handler
    cli_handler = CLIHandler(debug=config.debug_mode, display=display)
    
    # Parse command line arguments
    args = cli_handler.handle_arguments()
    
    # Use WorkflowManager for processing
    workflow = WorkflowManager(display=display, debug=config.debug_mode)
    workflow.process_workflow(
        input_path=args.input_path if not args.is_batch_mode else None,
        search_string=args.search_string,
        output_dir=args.output_dir,
        is_batch_mode=args.is_batch_mode
    )




if __name__ == "__main__":
    main()
