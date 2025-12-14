# API Documentation

This document provides detailed API documentation for the PDF Trimmer's key components and interfaces.

## Core Components

### PDFProcessor

The main class responsible for PDF processing and trimming operations.

```python
from src.core.pdf_processor import PDFProcessor

processor = PDFProcessor(debug=False, display_manager=display_manager)

result = processor.process_pdf(
    input_file="document.pdf",
    search_string="Chapter 5", 
    output_dir="output"
)

# Delete explicit pages/ranges
result = processor.process_pdf_delete_pages(
    input_file="document.pdf",
    delete_spec="1-4,7",
    output_dir="output",
)

# Delete before/after a page number (1-based)
result = processor.process_pdf_delete_before_after(
    input_file="document.pdf",
    before_page=10,   # deletes pages 1-9
    after_page=None,
    output_dir="output",
)
```

#### PDFProcessor Methods

- `process_pdf(input_file, search_string, output_dir) -> ProcessingResult`
  - Process a PDF file with trimming based on search string
  - Returns processing result with success status and output path
- `process_pdf_delete_pages(input_file, delete_spec, output_dir) -> ProcessingResult`
    - Delete specific pages/ranges from a PDF (1-based spec like `"1-4,7"`)
- `process_pdf_delete_before_after(input_file, before_page, after_page, output_dir) -> ProcessingResult`
    - Delete pages before/after a 1-based page number (before and after may be combined)

### TextSearchEngine

Handles text search operations within PDF documents.

```python
from src.core.text_search import TextSearchEngine

engine = TextSearchEngine(debug=False, display_manager=display)
position = engine.find_text_position("document.pdf", "search_text")
```

#### TextSearchEngine Methods

- `find_text_position(pdf_path, search_string) -> Optional[Tuple[int, float]]`
  - Locate text within PDF and return (page_number, y_position)
  - Returns None if text not found

### FileService

Manages file operations, validation, and path generation.

```python
from src.services.file_service import FileService

service = FileService(debug=False, display_manager=display)

# Find PDF files
files = service.find_pdf_files(directory=".")

# Validate input
validated_path = service.validate_input_file("input.pdf")

# Generate output filename
output_path = service.create_output_filename("input.pdf", "output_dir")

# Ensure output directory exists
service.ensure_output_directory("output_dir")
```

#### FileService Methods

- `find_pdf_files(directory) -> List[str]`: Find all unprocessed PDF files
- `validate_input_file(filepath) -> str`: Validate and return absolute path
- `create_output_filename(input_file, output_dir) -> str`: Generate output path
- `ensure_output_directory(output_dir) -> str`: Create and validate output directory

### WorkflowManager

Orchestrates the complete PDF processing workflow.

```python
from src.services.workflow_manager import WorkflowManager
from src.models.operation_request import OperationRequest, OperationType

manager = WorkflowManager(
    display=display,
    processor=processor,
    file_manager=file_service,
    config=config
)

# Routed operation (preferred)
success = manager.process_request(
    OperationRequest(
        operation=OperationType.SEARCH,
        input_path="input.pdf",
        is_batch_mode=False,
        output_dir="output",
        search_string="search_text",
    )
)

# Backwards compatible API (string-based)
success = manager.process_operation(
    operation="delete",
    input_path="input.pdf",
    is_batch_mode=False,
    output_dir="output",
    delete_spec="1-4,7",
)
```

#### WorkflowManager Methods

- `process_request(request: OperationRequest) -> bool`: Preferred typed routing entrypoint
- `process_operation(operation, input_path, output_dir, is_batch_mode, ...) -> bool`: Backwards-compatible routing entrypoint
- `process_single_file(...)`, `process_batch(...)`, `process_workflow(...)`: Deprecated wrappers

## Data Models

### ProcessingResult

Represents the outcome of a PDF processing operation.

```python
from src.models.result import ProcessingResult

result = ProcessingResult(
    success=True,
    input_file="input.pdf",
    output_file="output.pdf", 
    message="(trimmed at page 5, blank pages removed)",
    operation="search",
    search_found=True,
    pages_trimmed=True,
    trim_page=5,
    blank_pages_removed=2,
)
```

#### ProcessingResult Properties

- `input_file: str`: Source file path
- `output_file: str`: Generated output file path
- `success: bool`: Whether processing succeeded
- `message: str`: Human-readable summary
- `operation: str`: Operation identifier (`"search"`, `"delete"`, `"before_after"`)
- `blank_pages_removed: int`: Number of blank pages removed

Search-trim fields:
- `pages_trimmed: bool`: Whether content was trimmed
- `trim_page: Optional[int]`: 1-based page number where trimming occurred
- `search_found: Optional[bool]`: True if search term found, False if not found

Delete fields:
- `pages_deleted: int`: Number of pages deleted
- `deleted_pages: Optional[list[int]]`: 1-based deleted pages (sorted)
- `delete_spec: Optional[str]`: Echo of the delete specification for delete-by-spec
- `before_page: Optional[int]`, `after_page: Optional[int]`: Echo of before/after inputs

### ParsedArguments

Command-line argument parsing result.

```python
from src.ui.cli_handler import ParsedArguments

args = ParsedArguments(
    input_path="document.pdf",
    is_batch_mode=False,
    operation="search",
    search_string="Chapter 5",
)
```

#### ParsedArguments Properties

- `input_path: str`: Input file path (or `"."` in batch mode)
- `is_batch_mode: bool`: If True, process all PDFs in the current directory
- `operation: str`: One of `"search"`, `"delete"`, `"before_after"`
- `search_string: str`: Text to search for (search operation)
- `delete_spec: Optional[str]`: Page/range deletion spec (delete operation)
- `before_page: Optional[int]`, `after_page: Optional[int]`: Before/after delete page numbers

### PDFDocument

Enhanced wrapper around PyMuPDF document objects.

```python
from src.models.pdf_document import PDFDocument

# Open document
with PDFDocument("input.pdf") as doc:
    print(f"Pages: {len(doc)}")
    
    # Access pages
    page = doc[0]  # Get first page
    
    # Insert content from another PDF
    doc.insert_pdf(other_doc, start_at=5)
    
    # Save modified document
    doc.save("output.pdf")
```

#### PDFDocument Methods

- `open(file_path) -> PDFDocument`: Open PDF file
- `save(output_path)`: Save document to file
- `__len__() -> int`: Get number of pages
- `__getitem__(page_num) -> Page`: Get page by index
- `insert_pdf(other_doc, start_at, from_page, to_page)`: Insert pages
- `delete_page(page_num)`: Remove a page
- `search_text(text) -> List[tuple]`: Search across all pages

### Page

Enhanced wrapper around PyMuPDF page objects.

```python
from src.models.page import Page

page = doc[0]  # Get from PDFDocument

# Get page properties
rect = page.rect
text = page.get_text()
is_empty = page.is_blank()
```

#### Page Properties

- `rect: fitz.Rect`: Page rectangle/dimensions

#### Page Methods

- `get_text(option="text") -> str`: Extract text content
- `is_blank() -> bool`: Check if page is blank or decorative

## Configuration

### Config

Central configuration management with environment variable support.

```python
from src.config.settings import Config, config

# Use global instance
print(config.output_dir)
print(config.debug_mode)

# Create custom instance
custom_config = Config()
custom_config.debug_mode = True
```

#### Config Properties

- `debug_mode: bool`: Debug logging enabled (settable)
- `output_dir: str`: Default output directory (read-only)
- `output_suffix: str`: Output file suffix (read-only)
- `pdf_pattern: str`: PDF file search pattern (read-only)
- `processed_suffix: str`: Processed file suffix pattern (read-only)

#### Environment Variables

- `PDF_TRIMMER_DEBUG`: Set debug mode
- `PDF_TRIMMER_OUTPUT_DIR`: Set output directory
- `PDF_TRIMMER_OUTPUT_SUFFIX`: Set output suffix
- `PDF_TRIMMER_PDF_PATTERN`: Set PDF search pattern
- `PDF_TRIMMER_PROCESSED_SUFFIX`: Set processed file suffix

## Dependency Injection

### DependencyContainer

Manages component creation and wiring.

```python
from src.di.container import DependencyContainer, create_container_with_debug

# Create container
container = DependencyContainer(debug_mode=True)

# Resolve components
processor = container.resolve(IPDFProcessor)
file_service = container.resolve(IFileManager)

# Helper function
container = create_container_with_debug(debug_enabled=True)
```

#### DependencyContainer Methods

- `resolve(interface) -> T`: Get component instance
- `register_singleton(interface, factory)`: Register component factory

### Interfaces

The system uses abstract interfaces for dependency injection:

- `IPDFProcessor`: PDF processing operations
- `ITextSearchEngine`: Text search functionality  
- `IFileManager`: File operations
- `IDisplayManager`: Output and logging
- `ICLIHandler`: Command-line interface
- `IConfig`: Configuration access
- `IApplicationController`: Main application coordination

## Display and Logging

### DisplayManager

Handles all output formatting and logging.

```python
from src.ui.display import DisplayManager, DisplayConfig

config = DisplayConfig(debug_enabled=True, use_colors=True)
display = DisplayManager(config)

# Logging methods
display.info("Processing started")
display.success("File processed successfully")
display.warning("Potential issue detected") 
display.error("Processing failed")
display.debug("Detailed debug information")
```

#### DisplayManager Methods

- `info(message, **kwargs)`: Informational message
- `success(message, **kwargs)`: Success message
- `warning(message, **kwargs)`: Warning message
- `error(message, **kwargs)`: Error message
- `debug(message, **kwargs)`: Debug message (only shown in debug mode)

## Error Handling

### FileValidationError

Raised when file operations fail validation.

```python
from src.services.file_service import FileValidationError

try:
    service.validate_input_file("nonexistent.pdf")
except FileValidationError as e:
    print(f"File validation failed: {e}")
```

## Usage Examples

### Basic Processing

```python
# Create container and get components
container = create_container_with_debug(debug_enabled=False)
controller = container.resolve(IApplicationController)

# Process with command-line args
exit_code = controller.run(["document.pdf", "Chapter 5"])
```

Updated CLI style (recommended):

```python
exit_code = controller.run(["-f", "document.pdf", "-s", "Chapter 5"])
```

Delete examples:

```python
exit_code = controller.run(["-f", "document.pdf", "-d", "1-4,7"])
exit_code = controller.run(["-f", "document.pdf", "-b", "10"])  # delete pages 1-9
exit_code = controller.run(["-f", "document.pdf", "-a", "10"])  # delete pages 11-end
```

### Custom Processing Pipeline

```python
# Manual component setup
processor = container.resolve(IPDFProcessor)
file_service = container.resolve(IFileManager)

# Process single file
files = file_service.find_pdf_files("input_dir")
for pdf_file in files:
    result = processor.process_pdf(pdf_file, "search_text", "output_dir")
    if result.success:
        print(f"Processed: {result.output_file}")
```

### Configuration Customization

```python
# Environment-based configuration
import os
os.environ["PDF_TRIMMER_DEBUG"] = "true"
os.environ["PDF_TRIMMER_OUTPUT_DIR"] = "custom_output"

# Use global config
from src.config.settings import config
container = create_container_with_debug(config.debug_mode)
```
