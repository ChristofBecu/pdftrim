"""
Dependency injection system for PDF Trimmer.

This module implements a lightweight dependency injection container that manages
component creation, wiring, and lifecycle. The system uses abstract interfaces
to define contracts and concrete implementations for clean architecture.

Key Features:
- Interface-based dependency resolution
- Singleton component lifecycle management
- Debug mode configuration propagation
- Clean separation between interfaces and implementations

Components:
- DependencyContainer: Main IoC container for component resolution
- Abstract interfaces: Define contracts for all major components
- Factory functions: Handle complex component initialization

Usage:
    from src.di.container import create_container_with_debug
    from src.di.interfaces import IPDFProcessor
    
    container = create_container_with_debug(debug_enabled=False)
    processor = container.resolve(IPDFProcessor)
    
The dependency injection system ensures all components receive their dependencies
automatically and supports easy testing through interface mocking.
"""