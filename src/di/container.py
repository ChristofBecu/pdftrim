"""
Dependency injection container for PDF Trimmer.

This module provides a centralized dependency injection container that handles
component creation, wiring, and lifecycle management throughout the application.
"""

from typing import Optional, Dict, Any, TypeVar, Type, Callable, cast
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
    factory: Callable[[], Any]
    singleton: bool = True
    instance: Optional[Any] = None


class DependencyContainer:
    """
    Centralized dependency injection container.
    
    Manages component creation, wiring, and lifecycle throughout the application.
    Supports both singleton and transient lifetimes.
    """
    
    def __init__(self):
        """Initialize the dependency container."""
        self._registrations: Dict[Type, ComponentRegistration] = {}
        self._singletons: Dict[Type, Any] = {}
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
    
    def register_transient(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a component as transient (new instance each time).
        
        Args:
            interface: The interface/type to register
            factory: Factory function to create the component
        """
        self._registrations[interface] = ComponentRegistration(
            factory=factory,
            singleton=False
        )
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a specific instance.
        
        Args:
            interface: The interface/type to register
            instance: The specific instance to use
        """
        self._registrations[interface] = ComponentRegistration(
            factory=lambda: instance,
            singleton=True,
            instance=instance
        )
        self._singletons[interface] = instance
    
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
                return self._singletons[interface]
            
            # Create and cache singleton
            instance = registration.factory()
            self._singletons[interface] = instance
            return instance
        else:
            # Create new transient instance
            return registration.factory()
    
    def _register_default_components(self) -> None:
        """Register default component factories."""
        
        # Register Config as singleton
        self.register_singleton(IConfig, lambda: Config())
        
        # Register DisplayManager as singleton with proper configuration
        def create_display_manager() -> DisplayManager:
            config = self.resolve(IConfig)
            display_config = DisplayConfig(debug_enabled=config.debug_mode)
            return DisplayManager(display_config)
        
        self.register_singleton(IDisplayManager, create_display_manager)
        
        # Register FileService as singleton
        def create_file_manager() -> FileService:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            # Cast to concrete type for constructor
            display_manager = cast(DisplayManager, display)
            return FileService(debug=config.debug_mode, display_manager=display_manager)
        
        self.register_singleton(IFileManager, create_file_manager)
        
        # Register TextSearchEngine as singleton
        def create_text_search_engine() -> TextSearchEngine:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            # Cast to concrete type for constructor
            display_manager = cast(DisplayManager, display)
            return TextSearchEngine(debug=config.debug_mode, display_manager=display_manager)
        
        self.register_singleton(ITextSearchEngine, create_text_search_engine)
        
        # Register PDFProcessor as singleton
        def create_pdf_processor() -> PDFProcessor:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            # Cast to concrete type for constructor
            display_manager = cast(DisplayManager, display)
            return PDFProcessor(debug=config.debug_mode, display_manager=display_manager)
        
        self.register_singleton(IPDFProcessor, create_pdf_processor)
        
        # Register CLIHandler as singleton
        def create_cli_handler() -> CLIHandler:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            # Cast to concrete type for constructor
            display_manager = cast(DisplayManager, display)
            return CLIHandler(debug=config.debug_mode, display=display_manager)
        
        self.register_singleton(ICLIHandler, create_cli_handler)
        
        # Register ApplicationController as singleton
        def create_application_controller() -> ApplicationController:
            cli_handler = self.resolve(ICLIHandler)
            display = self.resolve(IDisplayManager)
            file_manager = self.resolve(IFileManager)
            processor = self.resolve(IPDFProcessor)
            config = self.resolve(IConfig)
            
            # Cast to concrete types for constructor
            cli_handler_concrete = cast(CLIHandler, cli_handler)
            display_concrete = cast(DisplayManager, display)
            file_manager_concrete = cast(FileManager, file_manager)
            processor_concrete = cast(PDFProcessor, processor)
            config_concrete = cast(Config, config)
            
            return ApplicationController(
                cli_handler=cli_handler_concrete,
                display=display_concrete,
                file_manager=file_manager_concrete,
                processor=processor_concrete,
                config=config_concrete
            )
        
        self.register_singleton(IApplicationController, create_application_controller)
    
    def create_config_with_debug(self, debug_mode: bool) -> 'DependencyContainer':
        """
        Create a new container with debug mode override.
        
        Args:
            debug_mode: Debug mode setting
            
        Returns:
            New container with debug mode configured
        """
        new_container = DependencyContainer()
        
        # Create config with debug override
        config = Config()
        config.debug_mode = debug_mode
        new_container.register_instance(IConfig, config)
        
        # Re-register other components with the new config
        new_container._register_dependent_components()
        
        return new_container
    
    def _register_dependent_components(self) -> None:
        """Register components that depend on config after config is set."""
        
        # Register DisplayManager with current config
        def create_display_manager() -> IDisplayManager:
            config = self.resolve(IConfig)
            display_config = DisplayConfig(debug_enabled=config.debug_mode)
            return DisplayManager(display_config)
        
        self.register_singleton(IDisplayManager, create_display_manager)
        
        # Register other components that depend on config and display
        def create_file_manager() -> FileService:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            display_manager = cast(DisplayManager, display)
            return FileService(debug=config.debug_mode, display_manager=display_manager)
        
        self.register_singleton(IFileManager, create_file_manager)
        
        def create_text_search_engine() -> TextSearchEngine:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            display_manager = cast(DisplayManager, display)
            return TextSearchEngine(debug=config.debug_mode, display_manager=display_manager)
        
        self.register_singleton(ITextSearchEngine, create_text_search_engine)
        
        def create_pdf_processor() -> PDFProcessor:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            display_manager = cast(DisplayManager, display)
            return PDFProcessor(debug=config.debug_mode, display_manager=display_manager)
        
        self.register_singleton(IPDFProcessor, create_pdf_processor)
        
        def create_cli_handler() -> CLIHandler:
            config = self.resolve(IConfig)
            display = self.resolve(IDisplayManager)
            display_manager = cast(DisplayManager, display)
            return CLIHandler(debug=config.debug_mode, display=display_manager)
        
        self.register_singleton(ICLIHandler, create_cli_handler)
        
        # Register ApplicationController as singleton
        def create_application_controller() -> ApplicationController:
            cli_handler = self.resolve(ICLIHandler)
            display = self.resolve(IDisplayManager)
            file_manager = self.resolve(IFileManager)
            processor = self.resolve(IPDFProcessor)
            config = self.resolve(IConfig)
            
            # Cast to concrete types for constructor
            cli_handler_concrete = cast(CLIHandler, cli_handler)
            display_concrete = cast(DisplayManager, display)
            file_manager_concrete = cast(FileService, file_manager)
            processor_concrete = cast(PDFProcessor, processor)
            config_concrete = cast(Config, config)
            
            return ApplicationController(
                cli_handler=cli_handler_concrete,
                display=display_concrete,
                file_manager=file_manager_concrete,
                processor=processor_concrete,
                config=config_concrete
            )
        
        self.register_singleton(IApplicationController, create_application_controller)
    
    def is_registered(self, interface: Type) -> bool:
        """
        Check if an interface is registered.
        
        Args:
            interface: The interface to check
            
        Returns:
            True if registered, False otherwise
        """
        return interface in self._registrations
    
    def clear(self) -> None:
        """Clear all registrations and singletons."""
        self._registrations.clear()
        self._singletons.clear()
    
    def get_registered_interfaces(self) -> Dict[Type, bool]:
        """
        Get all registered interfaces and their singleton status.
        
        Returns:
            Dictionary mapping interfaces to their singleton status
        """
        return {
            interface: registration.singleton 
            for interface, registration in self._registrations.items()
        }


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
    return DependencyContainer().create_config_with_debug(debug_mode)