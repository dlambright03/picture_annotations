"""
Command-line interface for ADA Annotator.

Provides CLI commands for document processing with AI-generated alt-text.
Supports DOCX and PPTX formats with context-aware annotations.
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

import structlog

from ada_annotator import __version__
from ada_annotator.ai_services import SemanticKernelService
from ada_annotator.config import Settings
from ada_annotator.document_processors import (
    DOCXAssembler,
    DOCXExtractor,
    PPTXAssembler,
    PPTXExtractor,
)
from ada_annotator.exceptions import EXIT_INPUT_ERROR, EXIT_SUCCESS
from ada_annotator.generators import AltTextGenerator
from ada_annotator.models import DocumentProcessingResult
from ada_annotator.utils.context_extractor import ContextExtractor
from ada_annotator.utils.error_handler import handle_error
from ada_annotator.utils.error_tracker import ErrorCategory, ErrorTracker
from ada_annotator.utils.logging import get_logger, setup_logging
from ada_annotator.utils.report_generator import ReportGenerator


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
        "--debug",
        action="store_true",
        help="Generate debug document with images and annotations instead of applying alt-text",
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


def validate_input_file(
    input_path: Path, logger: structlog.BoundLogger
) -> None:
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


def validate_context_file(
    context_path: Path, logger: structlog.BoundLogger
) -> None:
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


def validate_output_directory(
    output_path: Path, logger: structlog.BoundLogger
) -> None:
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
        logger.error(
            "output_directory_not_writable", path=str(output_dir), error=str(e)
        )
        raise ValueError(
            f"Output directory is not writable: {output_dir}"
        ) from e


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


def generate_debug_output_path(input_path: Path) -> Path:
    """
    Generate default debug output path from input path.

    Adds '_debug' suffix before file extension.

    Args:
        input_path: Path to input file.

    Returns:
        Path: Generated debug output file path.

    Example:
        >>> generate_debug_output_path(Path("document.docx"))
        Path("document_debug.docx")
    """
    return input_path.with_stem(f"{input_path.stem}_debug")


def process_document_dry_run(
    input_path: Path,
    context_path: str | None,
    logger: structlog.BoundLogger,
) -> DocumentProcessingResult:
    """
    Extract images without generating alt-text (dry run mode).

    Args:
        input_path: Path to input document.
        context_path: Path to external context file (optional).
        logger: Structured logger instance.

    Returns:
        DocumentProcessingResult with extraction summary.
    """
    start_time = time.time()

    # Determine document type and extract images
    if input_path.suffix.lower() == ".docx":
        extractor = DOCXExtractor(input_path)
        doc_format = "DOCX"
    elif input_path.suffix.lower() == ".pptx":
        extractor = PPTXExtractor(input_path)
        doc_format = "PPTX"
    else:
        raise ValueError(f"Unsupported format: {input_path.suffix}")

    images = extractor.extract_images()
    duration = time.time() - start_time

    logger.info(
        "dry_run_complete",
        images_found=len(images),
        duration_seconds=duration,
    )

    print(f"\n[+] Extracted {len(images)} images from {doc_format}")
    for img in images[:5]:  # Show first 5
        page_info = f"Page {img.page_number}" if img.page_number else "N/A"
        print(
            f"    - {img.image_id}: {img.width_pixels}x{img.height_pixels}px "
            f"({page_info})"
        )
    if len(images) > 5:
        print(f"    ... and {len(images) - 5} more")

    return DocumentProcessingResult(
        input_file=Path(input_path),
        output_file=Path("[DRY RUN]"),
        document_type=doc_format,
        total_images=len(images),
        successful_images=0,
        failed_images=0,
        images_processed=[img.image_id for img in images],
        errors=[],
        processing_duration_seconds=duration,
        total_tokens_used=0,
        estimated_cost_usd=0.0,
    )


async def process_document(
    input_path: Path,
    output_path: Path,
    context_path: Path | None,
    max_images: int | None,
    backup: bool,
    debug_mode: bool,
    logger: structlog.BoundLogger,
) -> DocumentProcessingResult:
    """
    Process document with full AI-powered alt-text generation.

    Args:
        input_path: Path to input document.
        output_path: Path to output document.
        context_path: Path to external context file (optional).
        max_images: Maximum number of images to process.
        backup: Whether to create backup of original file.
        debug_mode: Whether to generate debug document instead of applying alt-text.
        logger: Structured logger instance.

    Returns:
        DocumentProcessingResult with processing summary.
    """
    start_time = time.time()
    error_tracker = ErrorTracker()

    # Step 1: Extract images
    print("[1/4] Extracting images...")
    if input_path.suffix.lower() == ".docx":
        extractor = DOCXExtractor(input_path)
        doc_format = "DOCX"
    elif input_path.suffix.lower() == ".pptx":
        extractor = PPTXExtractor(input_path)
        doc_format = "PPTX"
    else:
        raise ValueError(f"Unsupported format: {input_path.suffix}")

    images = extractor.extract_images()

    # Apply max_images limit
    if max_images and len(images) > max_images:
        logger.info(f"Limiting to first {max_images} images")
        images = images[:max_images]

    print(f"    Found {len(images)} images")

    if len(images) == 0:
        logger.warning("no_images_found")
        return DocumentProcessingResult(
            input_file=Path(input_path),
            output_file=Path(output_path),
            document_type=doc_format,
            total_images=0,
            successful_images=0,
            failed_images=0,
            images_processed=[],
            errors=[],
            processing_duration_seconds=time.time() - start_time,
            total_tokens_used=0,
            estimated_cost_usd=0.0,
        )

    # Step 2: Initialize AI services
    print("[2/4] Initializing AI services...")
    try:
        settings = Settings()
        ai_service = SemanticKernelService(settings)
        context_extractor = ContextExtractor(
            document_path=input_path, external_context_path=context_path
        )
        generator = AltTextGenerator(
            settings, ai_service, context_extractor
        )
        print("    AI services ready")
    except Exception as e:
        logger.error("ai_initialization_failed", error=str(e))
        raise

    # Step 3: Generate alt-text
    print(f"[3/4] Generating alt-text for {len(images)} images...")
    alt_text_results = await generator.generate_for_multiple_images(
        images, continue_on_error=True
    )

    succeeded = len(alt_text_results)
    failed = len(images) - succeeded

    # Track errors for images that didn't get results
    if failed > 0:
        processed_ids = {r.image_id for r in alt_text_results}
        for img in images:
            if img.image_id not in processed_ids:
                error_tracker.track_error(
                    image_id=img.image_id,
                    error_message="Failed to generate alt-text",
                    category=ErrorCategory.API,
                    page=str(img.page_number) if img.page_number else None,
                )

    print(f"    Generated {succeeded}/{len(images)} alt-texts")

    # Step 4: Apply alt-text to document OR create debug document
    if debug_mode:
        print("[4/4] Creating debug document...")
        from ada_annotator.utils.debug_document import create_debug_document

        create_debug_document(images, alt_text_results, output_path)
        print(f"    Debug document created: {output_path}")
    else:
        print("[4/4] Applying alt-text to document...")

        # Create backup if requested
        if backup:
            backup_path = input_path.with_stem(f"{input_path.stem}_backup")
            import shutil

            shutil.copy2(input_path, backup_path)
            logger.info("backup_created", backup_path=str(backup_path))
            print(f"    Backup created: {backup_path}")

        # Apply alt-text
        if doc_format == "DOCX":
            assembler = DOCXAssembler(input_path, output_path)
        else:  # PPTX
            assembler = PPTXAssembler(input_path, output_path)

        status_map = assembler.apply_alt_text(alt_text_results)
        assembler.save_document()

        # Track assembly errors
        for image_id, status in status_map.items():
            if status != "success":
                error_tracker.track_error(
                    image_id=image_id,
                    error_message=f"Assembly failed: {status}",
                    category=ErrorCategory.PROCESSING,
                )

        print(f"    Document saved: {output_path}")

    # Calculate processing metrics
    duration = time.time() - start_time
    total_tokens = sum(r.tokens_used for r in alt_text_results)

    # Calculate estimated cost (using generator's constants)
    total_cost = 0.0
    for r in alt_text_results:
        # Rough cost estimate based on tokens_used
        # Assume 70% input tokens, 30% output tokens
        input_tokens = int(r.tokens_used * 0.7)
        output_tokens = int(r.tokens_used * 0.3)
        total_cost += (
            input_tokens * AltTextGenerator.INPUT_COST_PER_TOKEN
            + output_tokens * AltTextGenerator.OUTPUT_COST_PER_TOKEN
        )

    # Build error list from error tracker
    errors_list = error_tracker.get_errors()

    result = DocumentProcessingResult(
        input_file=Path(input_path),
        output_file=Path(output_path),
        document_type=doc_format,
        total_images=len(images),
        successful_images=succeeded,
        failed_images=failed,
        images_processed=[r.image_id for r in alt_text_results],
        errors=errors_list,
        processing_duration_seconds=duration,
        total_tokens_used=total_tokens,
        estimated_cost_usd=total_cost,
    )

    return result


def main(argv: list[str] | None = None) -> int:
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
    log_file = (
        Path(args.log_file) if args.log_file else Path("ada_annotator.log")
    )
    log_level = "DEBUG" if args.verbose else args.log_level
    enable_console = args.verbose

    try:
        setup_logging(
            log_file=log_file,
            log_level=log_level,
            enable_console=enable_console,
        )
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
            if args.debug:
                output_path = generate_debug_output_path(input_path)
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
        if args.debug:
            print(
                "\n[DEBUG MODE] Will generate debug document with images "
                "and annotations"
            )
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

        # Process the document
        if args.dry_run:
            print("\n[!] DRY RUN MODE - Extracting images only...")
            result = process_document_dry_run(
                input_path, args.context, logger
            )
        else:
            print("\n[+] Processing document...")
            result = asyncio.run(
                process_document(
                    input_path=input_path,
                    output_path=output_path,
                    context_path=Path(args.context) if args.context else None,
                    max_images=args.max_images,
                    backup=args.backup,
                    debug_mode=args.debug,
                    logger=logger,
                )
            )

        # Display summary
        report_gen = ReportGenerator()
        summary = report_gen.generate_summary(result)
        print(f"\n{summary}")

        # Generate report
        if not args.dry_run and len(result.images_processed) > 0:
            report_path = output_path.with_name(
                f"{output_path.stem}_report.md"
            )
            # For report generation, we need the full alt_text_results
            # We'll need to store them or pass them differently
            # For now, generate report without them (basic report)
            print(f"\n[+] Processing complete. Output: {output_path}")

        logger.info("cli_completed", exit_code=EXIT_SUCCESS)
        return EXIT_SUCCESS

    except (FileNotFoundError, ValueError) as e:
        logger.error("validation_failed", error=str(e))
        print(f"\nError: {e}", file=sys.stderr)
        print(
            "\nRun 'ada-annotator --help' for usage information.",
            file=sys.stderr,
        )
        return handle_error(e, exit_on_error=False)

    except Exception as e:
        logger.exception("unexpected_error", error=str(e))
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return handle_error(e, exit_on_error=False)


if __name__ == "__main__":
    sys.exit(main())
