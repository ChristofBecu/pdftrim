#!/bin/bash
# Wrapper script to run pdftrim.py with the correct Python environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ -f "$VENV_PYTHON" ]; then
    exec "$VENV_PYTHON" "$SCRIPT_DIR/pdftrim.py" "$@"
else
    echo "Error: Virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Please run: python -m venv .venv && source .venv/bin/activate && pip install PyMuPDF PyPDF2 pdfminer.six"
    exit 1
fi
