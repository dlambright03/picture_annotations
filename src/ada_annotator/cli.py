"""
Command-line interface for ADA Annotator.

Provides CLI commands for document processing with AI-generated alt-text.
Supports DOCX and PPTX formats with context-aware annotations.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import structlog

from ada_annotator import __version__
from ada_annotator.config import get_settings
from ada_annotator.exceptions import EXIT_SUCCESS, EXIT_INPUT_ERROR
from ada_annotator.utils.error_handler import handle_error
from ada_annotator.utils.logging import setup_logging, get_logger


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for CLI.

    Returns:
        argparse.ArgumentParser: Configured argument parser with all CLI options.
    """
    parser = argparse.ArgumentParser(
        prog="ada-annotator",
        description="ADA Annotator - Automatically generate alt-text for images in documents",
        epilog="For more information, visit: https://github.com/yourusername/ada-annotator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Required positional argument
    parser.add_argument(
        "input",
        type=str,
        metavar="INPUT_FILE",
        help="Path to input document file (DOCX or PPTX)",
    )

    # Optional arguments
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="OUTPUT_FILE",
        help="Path to output file (default: INPUT_annotated.EXT)",
    )

    parser.add_argument(
        "-c",
        "--context",
        type=str,
        metavar="CONTEXT_FILE",
        help="Path to external context file (TXT or MD) to enhance alt-text generation",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging to console (DEBUG level)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview processing without modifying or creating any files",
    )

    parser.add_argument(
        "-b",
        "--backup",
        action="store_true",
        help="Create backup of original file before processing",
    )

    parser.add_argument(
        "--config",
        type=str,
        metavar="CONFIG_FILE",
        help="Path to custom configuration JSON file (default: config.json)",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        metavar="LOG_FILE",
        help="Path to log file (default: ada_annotator.log)",
    )

    parser.add_argument(
        "--max-images",
        type=int,
        metavar="N",
        help="Maximum number of images to process (default: unlimited)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    return parser


def validate_input_file(input_path: Path, logger: structlog.BoundLogger) -> None:
    """
    Validate input file exists and is a supported format.

    Args:
        input_path: Path to input file.
        logger: Structured logger instance.

    Raises:
        FileNotFoundError: If input file does not exist.
        ValueError: If input file format is not supported.
    """
    # Check file exists
    if not input_path.exists():
        logger.error("input_file_not_found", path=str(input_path))
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.is_file():
        logger.error("input_path_not_file", path=str(input_path))
        raise ValueError(f"Input path is not a file: {input_path}")

    # Check supported format
    supported_extensions = [".docx", ".pptx"]
    if input_path.suffix.lower() not in supported_extensions:
        logger.error(
            "unsupported_file_format",
            path=str(input_path),
            extension=input_path.suffix,
            supported=supported_extensions,
        )
        raise ValueError(
            f"Unsupported file format: {input_path.suffix}. "
            f"Supported formats: {', '.join(supported_extensions)}"
        )

    logger.info(
        "input_file_validated",
        path=str(input_path),
        format=input_path.suffix.upper(),
        size_bytes=input_path.stat().st_size,
    )


def validate_context_file(context_path: Path, logger: structlog.BoundLogger) -> None:
    """
    Validate context file exists and is a supported format.

    Args:
        context_path: Path to context file.
        logger: Structured logger instance.

    Raises:
        FileNotFoundError: If context file does not exist.
        ValueError: If context file format is not supported.
    """
    if not context_path.exists():
        logger.error("context_file_not_found", path=str(context_path))
        raise FileNotFoundError(f"Context file not found: {context_path}")

    if not context_path.is_file():
        logger.error("context_path_not_file", path=str(context_path))
        raise ValueError(f"Context path is not a file: {context_path}")

    # Check supported format
    supported_extensions = [".txt", ".md"]
    if context_path.suffix.lower() not in supported_extensions:
        logger.error(
            "unsupported_context_format",
            path=str(context_path),
            extension=context_path.suffix,
            supported=supported_extensions,
        )
        raise ValueError(
            f"Unsupported context file format: {context_path.suffix}. "
            f"Supported formats: {', '.join(supported_extensions)}"
        )

    logger.info(
        "context_file_validated",
        path=str(context_path),
        size_bytes=context_path.stat().st_size,
    )


def validate_output_directory(output_path: Path, logger: structlog.BoundLogger) -> None:
    """
    Validate output directory is writable.

    Args:
        output_path: Path to output file.
        logger: Structured logger instance.

    Raises:
        ValueError: If output directory does not exist or is not writable.
    """
    output_dir = output_path.parent

    if not output_dir.exists():
        logger.error("output_directory_not_found", path=str(output_dir))
        raise ValueError(f"Output directory does not exist: {output_dir}")

    # Test write permission by attempting to create a temporary file
    try:
        test_file = output_dir / ".ada_annotator_write_test"
        test_file.touch()
        test_file.unlink()
        logger.debug("output_directory_writable", path=str(output_dir))
    except (PermissionError, OSError) as e:
        logger.error("output_directory_not_writable", path=str(output_dir), error=str(e))
        raise ValueError(f"Output directory is not writable: {output_dir}")


def generate_output_path(input_path: Path) -> Path:
    """
    Generate default output path from input path.

    Adds '_annotated' suffix before file extension.

    Args:
        input_path: Path to input file.

    Returns:
        Path: Generated output file path.

    Example:
        >>> generate_output_path(Path("document.docx"))
        Path("document_annotated.docx")
    """
    return input_path.with_stem(f"{input_path.stem}_annotated")


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        argv: Command-line arguments (for testing). If None, uses sys.argv.

    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args(argv)

    # Setup logging
    log_file = Path(args.log_file) if args.log_file else Path("ada_annotator.log")
    log_level = "DEBUG" if args.verbose else args.log_level
    enable_console = args.verbose

    try:
        setup_logging(log_file=log_file, log_level=log_level, enable_console=enable_console)
    except ValueError as e:
        print(f"Error: Invalid log level: {e}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    logger = get_logger(__name__)
    logger.info(
        "cli_started",
        version=__version__,
        args=vars(args),
    )

    try:
        # Validate input file
        input_path = Path(args.input)
        validate_input_file(input_path, logger)

        # Generate or validate output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = generate_output_path(input_path)
            logger.info("output_path_generated", path=str(output_path))

        # Validate output directory
        validate_output_directory(output_path, logger)

        # Validate context file if provided
        if args.context:
            context_path = Path(args.context)
            validate_context_file(context_path, logger)

        # Display processing summary
        print(f"\nADA Annotator v{__version__}")
        print("=" * 70)
        print(f"Input File:    {input_path}")
        print(f"Output File:   {output_path}")
        if args.context:
            print(f"Context File:  {args.context}")
        if args.dry_run:
            print("\n[!] DRY RUN MODE - No files will be modified")
        if args.backup:
            print("\n[+] Backup will be created before processing")
        print("=" * 70)

        logger.info(
            "validation_complete",
            input_path=str(input_path),
            output_path=str(output_path),
            context_path=args.context,
            dry_run=args.dry_run,
            backup=args.backup,
        )

        # TODO: Implement actual document processing in Phase 1.3+
        print("\n[!] Document processing not yet implemented (Phase 1.3+)")
        print("[+] Arguments validated successfully")

        if not args.dry_run:
            print(f"\nNext steps:")
            print(f"  1. Extract images from {input_path.suffix.upper()}")
            print(f"  2. Generate alt-text with AI")
            print(f"  3. Apply annotations to output file")

        logger.info("cli_completed", exit_code=EXIT_SUCCESS)
        return EXIT_SUCCESS

    except (FileNotFoundError, ValueError) as e:
        logger.error("validation_failed", error=str(e))
        print(f"\nError: {e}", file=sys.stderr)
        print("\nRun 'ada-annotator --help' for usage information.", file=sys.stderr)
        return handle_error(e, exit_on_error=False)

    except Exception as e:
        logger.exception("unexpected_error", error=str(e))
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return handle_error(e, exit_on_error=False)


if __name__ == "__main__":
    sys.exit(main())
