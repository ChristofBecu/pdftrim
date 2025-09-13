#!/usr/bin/env python3
"""
PDF Trimmer - Removes pages from a PDF starting at a specific search string.
"""

from typing import cast

from src.di.container import create_container_with_debug, get_container
from src.di.interfaces import ICLIHandler, IDisplayManager, IFileManager, IPDFProcessor, IConfig
from src.workflow.workflow_manager import WorkflowManager
from src.config.settings import config
from src.cli.cli_handler import ParsedArguments


def main() -> None:
    """Main entry point using dependency injection."""
    
    # Create dependency container with debug mode from config
    container = create_container_with_debug(config.debug_mode)
    
    # Resolve dependencies
    cli_handler = container.resolve(ICLIHandler)
    display = container.resolve(IDisplayManager)
    file_manager = container.resolve(IFileManager)
    processor = container.resolve(IPDFProcessor)
    config_service = container.resolve(IConfig)
    
    # Parse command line arguments
    parsed_args = cli_handler.handle_arguments()
    # Cast to concrete type for attribute access
    args = cast(ParsedArguments, parsed_args)
    
    # Create WorkflowManager with injected dependencies
    workflow = WorkflowManager(
        display=display,
        processor=processor,
        file_manager=file_manager,
        cli_handler=cli_handler,
        config=config_service,
        debug=config_service.debug_mode
    )
    
    # Process workflow
    workflow.process_workflow(
        input_path=args.input_path if not args.is_batch_mode else None,
        search_string=args.search_string,
        output_dir=args.output_dir,
        is_batch_mode=args.is_batch_mode
    )


if __name__ == "__main__":
    main()
