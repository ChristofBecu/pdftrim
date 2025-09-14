"""
Dependency injection container for PDF Trimmer.

This module provides a centralized dependency injection container that handles
component creation, wiring, and lifecycle management throughout the application.
"""

from typing import Optional, Dict, TypeVar, Type, Callable, cast
from dataclasses import dataclass

from .interfaces import (
    IDisplayManager, IFileManager, ITextSearchEngine, 
    IPDFProcessor, ICLIHandler, IConfig, IApplicationController
)
from ..config.settings import Config
from ..ui.display import DisplayManager, DisplayConfig
from ..services.file_service import FileService
from ..core.text_search import TextSearchEngine
from ..core.pdf_processor import PDFProcessor
from ..ui.cli_handler import CLIHandler
from ..ui.controllers import ApplicationController


T = TypeVar('T')


@dataclass
class ComponentRegistration:
    """Registration information for a component."""
    factory: Callable[[], object]
    singleton: bool = True


class DependencyContainer:
    """
    Centralized dependency injection container.
    
    Manages component creation, wiring, and lifecycle throughout the application.
    """
    
    def __init__(self, debug_mode: Optional[bool] = None):
        """
        Initialize the dependency container.
        
        Args:
            debug_mode: Optional debug mode override
        """
        self._registrations: Dict[Type, ComponentRegistration] = {}
        self._singletons: Dict[Type, object] = {}
        self._debug_mode = debug_mode
        self._register_default_components()
    
    def register_singleton(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a component as a singleton.
        
        Args:
            interface: The interface/type to register
            factory: Factory function to create the component
        """
        self._registrations[interface] = ComponentRegistration(
            factory=factory,
            singleton=True
        )
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a component by its interface.
        
        Args:
            interface: The interface/type to resolve
            
        Returns:
            The resolved component instance
            
        Raises:
            ValueError: If the interface is not registered
        """
        if interface not in self._registrations:
            raise ValueError(f"Interface {interface.__name__} is not registered")
        
        registration = self._registrations[interface]
        
        if registration.singleton:
            # Return cached singleton if available
            if interface in self._singletons:
                return cast(T, self._singletons[interface])
            
            # Create and cache singleton
            instance = registration.factory()
            self._singletons[interface] = instance
            return cast(T, instance)
        else:
            # Create new transient instance
            return cast(T, registration.factory())
    
    def _register_default_components(self) -> None:
        """Register default component factories."""
        
        # Register Config as singleton with optional debug override
        def create_config() -> Config:
            config = Config()
            if self._debug_mode is not None:
                config.debug_mode = self._debug_mode
            return config
        
        self.register_singleton(IConfig, create_config)
        
        # Register DisplayManager as singleton with proper configuration
        def create_display_manager() -> DisplayManager:
            config = self.resolve(IConfig)
            display_config = DisplayConfig(debug_enabled=config.debug_mode)
            return DisplayManager(display_config)
        
        self.register_singleton(IDisplayManager, create_display_manager)
        
        # Register FileService as singleton
        def create_file_manager() -> FileService:
            config = self.resolve(IConfig)
            display = cast(DisplayManager, self.resolve(IDisplayManager))
            return FileService(debug=config.debug_mode, display_manager=display)
        
        self.register_singleton(IFileManager, create_file_manager)
        
        # Register TextSearchEngine as singleton
        def create_text_search_engine() -> TextSearchEngine:
            config = self.resolve(IConfig)
            display = cast(DisplayManager, self.resolve(IDisplayManager))
            return TextSearchEngine(debug=config.debug_mode, display_manager=display)
        
        self.register_singleton(ITextSearchEngine, create_text_search_engine)
        
        # Register PDFProcessor as singleton
        def create_pdf_processor() -> PDFProcessor:
            config = self.resolve(IConfig)
            display = cast(DisplayManager, self.resolve(IDisplayManager))
            return PDFProcessor(debug=config.debug_mode, display_manager=display)
        
        self.register_singleton(IPDFProcessor, create_pdf_processor)
        
        # Register CLIHandler as singleton
        def create_cli_handler() -> CLIHandler:
            config = self.resolve(IConfig)
            display = cast(DisplayManager, self.resolve(IDisplayManager))
            return CLIHandler(debug=config.debug_mode, display=display)
        
        self.register_singleton(ICLIHandler, create_cli_handler)
        
        # Register ApplicationController as singleton
        def create_application_controller() -> ApplicationController:
            cli_handler = cast(CLIHandler, self.resolve(ICLIHandler))
            display = cast(DisplayManager, self.resolve(IDisplayManager))
            file_manager = cast(FileService, self.resolve(IFileManager))
            processor = cast(PDFProcessor, self.resolve(IPDFProcessor))
            config = cast(Config, self.resolve(IConfig))
            
            return ApplicationController(
                cli_handler=cli_handler,
                display=display,
                file_manager=file_manager,
                processor=processor,
                config=config
            )
        
        self.register_singleton(IApplicationController, create_application_controller)


# Global default container instance
_default_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """
    Get the global default dependency container.
    
    Returns:
        The default dependency container instance
    """
    global _default_container
    if _default_container is None:
        _default_container = DependencyContainer()
    return _default_container


def set_container(container: DependencyContainer) -> None:
    """
    Set the global default dependency container.
    
    Args:
        container: The container to set as default
    """
    global _default_container
    _default_container = container


def create_container_with_debug(debug_mode: bool) -> DependencyContainer:
    """
    Create a dependency container with debug mode configured.
    
    Args:
        debug_mode: Whether to enable debug mode
        
    Returns:
        Configured dependency container
    """
    return DependencyContainer(debug_mode=debug_mode)