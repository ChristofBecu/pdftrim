# PDF Trimmer

A Python utility for trimming PDF documents based on text search patterns. Removes pages after a specified search string and automatically detects and removes blank pages.

## Features

- **Text-based trimming**: Remove pages starting from a specific search string
- **Page deletion**: Delete specific pages/ranges or pages before/after a page number
- **Blank page detection**: Automatically identify and remove blank or decorative pages
- **Batch processing**: Process multiple PDFs in a directory or single files
- **Flexible output**: Configurable output directory and file naming
- **Debug mode**: Detailed logging for troubleshooting
- **Environment configuration**: Customize behavior via environment variables

## Installation

### Requirements

- Python 3.10+ (tested with Python 3.13.7)
- PyMuPDF library for PDF processing

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install "PyMuPDF>=1.24.0,<2.0.0"
```

## Usage

### Basic Usage

```bash
# Process all PDFs in current directory (batch mode)
python pdftrim.py --search "search_string"

# Process a specific PDF file
python pdftrim.py --file input.pdf --search "search_string"

# Delete specific pages (1-based)
python pdftrim.py --file input.pdf --delete "1-4,7"

# Delete pages before a page number (1-based)
python pdftrim.py --file input.pdf --before 10   # deletes pages 1-9

# Delete pages after a page number (1-based)
python pdftrim.py --file input.pdf --after 10    # deletes pages 11-end

# Combine before + after (allowed)
python pdftrim.py --file input.pdf --before 10 --after 12
```

### Examples

```bash
# Remove pages after "Chapter 5" from all PDFs in directory
python pdftrim.py -s "Chapter 5"

# Process specific document, remove pages after "Appendix A"
python pdftrim.py -f document.pdf -s "Appendix A"

# Process with custom output directory
PDF_TRIMMER_OUTPUT_DIR=processed python pdftrim.py -s "References"

# Delete pages 1-4 and 7
python pdftrim.py -f document.pdf -d "1-4,7"

# Remove everything before page 10
python pdftrim.py -f document.pdf -b 10

# Remove everything after page 10
python pdftrim.py -f document.pdf -a 10
```

### Notes

- Page numbers are **1-based** for all page deletion flags.
- `--before` and `--after` can be combined; other operations are mutually exclusive.
- The tool refuses to create an empty PDF (if an operation would delete all pages).

### Command Line Options

- `--help`, `-h`: Show help message
- `--version`, `-v`: Show version information

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PDF_TRIMMER_DEBUG` | `false` | Enable debug output |
| `PDF_TRIMMER_OUTPUT_DIR` | `output` | Set output directory |
| `PDF_TRIMMER_OUTPUT_SUFFIX` | `_edit` | Set output file suffix |
| `PDF_TRIMMER_PDF_PATTERN` | `*.pdf` | PDF file search pattern |
| `PDF_TRIMMER_PROCESSED_SUFFIX` | `_edit.pdf` | Skip files with this suffix |

## How It Works

1. **Text Search**: Locates the specified search string in the PDF
2. **Page Trimming**: Removes all pages after the search string location
3. **Blank Detection**: Analyzes remaining pages for meaningful content
4. **Content Filtering**: Removes pages with minimal or decorative-only content
5. **Output Generation**: Saves processed PDF with configurable naming

### Blank Page Detection

The tool uses sophisticated algorithms to identify blank pages:

- **Text Analysis**: Checks for meaningful text content (>20 characters)
- **Content Blocks**: Analyzes text block structure and substance
- **Decorative Filtering**: Distinguishes between content and page decorations
- **Size Heuristics**: Considers page dimensions and content density

## Architecture

The PDF Trimmer follows a clean architecture with dependency injection:

```text
src/
├── core/           # Core processing logic
├── models/         # Data models and PDF wrappers
├── services/       # File and workflow management
├── ui/            # User interface and CLI handling
├── di/            # Dependency injection container
└── config/        # Configuration management
```

### Key Components

- **PDFProcessor**: Core PDF processing and trimming logic
- **TextSearchEngine**: Text location and analysis
- **FileService**: File operations and validation
- **WorkflowManager**: Orchestrates processing workflow
- **DisplayManager**: Output formatting and logging
- **DependencyContainer**: Component wiring and lifecycle

## Development

### Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

### Project Structure

```text
pdftrim/
├── pdftrim.py          # Main entry point
├── requirements.txt    # Dependencies
├── src/               # Source code
├── planning/          # Development documentation
└── output/           # Default output directory
```

### Code Quality

- **Type Hints**: Comprehensive type annotations throughout
- **Clean Architecture**: Separation of concerns with clear interfaces
- **Dependency Injection**: Testable and modular component design
- **Error Handling**: Robust error management with user-friendly messages

### Running in Debug Mode

```bash
# Enable debug logging
PDF_TRIMMER_DEBUG=true python pdftrim.py --search "search_string"

# Debug with custom settings
PDF_TRIMMER_DEBUG=true PDF_TRIMMER_OUTPUT_DIR=debug python pdftrim.py --file document.pdf --search "text"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Ensure code follows project style guidelines
5. Submit a pull request

### Development Dependencies

For development work, you may want additional tools:

```bash
# Type checking
pip install mypy

# Code formatting
pip install black

# Linting
pip install ruff

# Testing (when tests are added)
pip install pytest pytest-cov
```

## License

[Add your license information here]

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

For issues, questions, or contributions, please [create an issue](link-to-issues) or [start a discussion](link-to-discussions).
