#!/usr/bin/env python3
"""
PDF Trimmer - Removes pages from a PDF starting at a specific search string.

This is the main entry point that sets up dependency injection and delegates
all application logic to the ApplicationController.
"""

import sys

from src.di.container import create_container_with_debug
from src.di.interfaces import IApplicationController
from src.config.settings import config


def main() -> None:
    """Main entry point - thin orchestration layer."""
    
    # Create dependency injection container with current config
    container = create_container_with_debug(config.debug_mode)
    
    # Resolve the application controller
    app_controller = container.resolve(IApplicationController)
    
    # Run the application and exit with the returned code
    exit_code = app_controller.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
