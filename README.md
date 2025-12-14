# PDF Trimmer

A Python utility for trimming and editing PDF documents via a text search cutoff or explicit page deletion (ranges, before/after), with batch processing and automatic blank-page removal.

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

You can run via `python pdftrim.py ...`, or use the wrapper script `./pdftrim.sh ...` to automatically use the local virtualenv at `.venv`.

### Basic Usage

```bash
# Process all PDFs in current directory (batch mode)
python pdftrim.py --delete --search "search_string"
# or:
./pdftrim.sh --delete --search "search_string"

# Process a specific PDF file
python pdftrim.py --file input.pdf --delete --search "search_string"
# or:
./pdftrim.sh --file input.pdf --delete --search "search_string"

# Delete specific pages (1-based)
python pdftrim.py --file input.pdf --delete "1-4,7"

# Keep only specific pages (1-based) - inverse of delete-by-spec
python pdftrim.py --file input.pdf --keep "1-4,7"

# Invert before/after behavior (keep instead of delete)
python pdftrim.py --file input.pdf --keep --before 10   # keeps pages 1-9

# Delete pages before a page number (1-based)
python pdftrim.py --file input.pdf --delete --before 10   # deletes pages 1-9

# Delete pages after a page number (1-based)
python pdftrim.py --file input.pdf --delete --after 10    # deletes pages 11-end

# Combine before + after (allowed)
python pdftrim.py --file input.pdf --delete --before 10 --after 12

# Invert text-based trimming (keep content starting at the match)
python pdftrim.py --file input.pdf --keep --search "search_string"
```

### Examples

```bash
# Remove pages after "Chapter 5" from all PDFs in directory
python pdftrim.py -d -s "Chapter 5"

# Process specific document, remove pages after "Appendix A"
python pdftrim.py -f document.pdf -d -s "Appendix A"

# Process with custom output directory
PDF_TRIMMER_OUTPUT_DIR=processed python pdftrim.py -d -s "References"

# Delete pages 1-4 and 7
python pdftrim.py -f document.pdf -d "1-4,7"

# Keep only pages 1-4 and 7
python pdftrim.py -f document.pdf -k "1-4,7"

# Remove everything before page 10
python pdftrim.py -f document.pdf -d -b 10

# Remove everything after page 10
python pdftrim.py -f document.pdf -d -a 10
```

### Notes

- Page numbers are **1-based** for all page deletion flags (including `--keep`).
- For `--search`, `--before`, and `--after`, you must specify a mode flag: `--delete` or `--keep`.
- `--before` and `--after` can be combined; other operations are mutually exclusive.
- The tool refuses to create an empty PDF (if an operation would delete all pages).

### Command Line Options

- `-f`, `--file`: Input PDF file path (omit for batch mode in current directory)
- `-s`, `--search`: Trim based on the first occurrence of this search string (requires `--delete` or `--keep`)
- `-d`, `--delete`: Delete mode; with a spec deletes pages/ranges (e.g. `1-4,7`)
- `-k`, `--keep`: Keep mode; with a spec keeps pages/ranges (e.g. `1-4,7`)
- `-b`, `--before`: Before-page selection (requires `--delete` or `--keep`)
- `-a`, `--after`: After-page selection (requires `--delete` or `--keep`)
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
