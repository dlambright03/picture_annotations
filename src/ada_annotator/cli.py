"""
Command-line interface for ADA Annotator.

Provides CLI commands for document processing without the web UI.
"""

import sys
from pathlib import Path
from typing import Optional

import structlog

from ada_annotator import __version__
from ada_annotator.config import get_settings

logger = structlog.get_logger()


def main() -> None:
    """
    Main entry point for the CLI.

    This is a placeholder for future CLI implementation.
    For now, users should use the Streamlit web interface.
    """
    print(f"ADA Annotator v{__version__}")
    print("\nCLI mode is not yet implemented.")
    print("Please use the web interface:")
    print("  streamlit run src/ada_annotator/app.py")
    print("\nOr run Python directly:")
    print("  python -m ada_annotator.app")
    sys.exit(0)


if __name__ == "__main__":
    main()
