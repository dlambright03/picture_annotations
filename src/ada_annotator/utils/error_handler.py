"""
Error handling utilities for ADA Annotator.

Provides utilities for error handling, logging, and exit code
management.
"""

import sys
from collections.abc import Callable
from functools import wraps
from typing import TypeVar, cast

import structlog

from ada_annotator.exceptions import (
    EXIT_API_ERROR,
    EXIT_GENERAL_ERROR,
    EXIT_INPUT_ERROR,
    EXIT_VALIDATION_ERROR,
    ADAAnnotatorError,
    APIError,
    FileError,
    ProcessingError,
    ValidationError,
)

logger = structlog.get_logger(__name__)

# Type variable for generic function signatures
F = TypeVar("F", bound=Callable)


def get_exit_code(exception: Exception) -> int:
    """
    Get the appropriate exit code for an exception.

    Maps both custom and built-in exceptions to appropriate exit codes.

    Parameters:
        exception: The exception to get exit code for.

    Returns:
        int: Exit code (0-4).
    """
    # Custom exceptions
    if isinstance(exception, FileError):
        return EXIT_INPUT_ERROR
    elif isinstance(exception, APIError):
        return EXIT_API_ERROR
    elif isinstance(exception, ValidationError):
        return EXIT_VALIDATION_ERROR
    elif isinstance(exception, (ProcessingError, ADAAnnotatorError)):
        return EXIT_GENERAL_ERROR
    # Built-in exceptions
    elif isinstance(exception, FileNotFoundError):
        return EXIT_INPUT_ERROR
    elif isinstance(exception, ValueError):
        # ValueError used for validation failures (file format, etc.)
        return EXIT_INPUT_ERROR
    elif isinstance(exception, PermissionError):
        return EXIT_INPUT_ERROR
    else:
        return EXIT_GENERAL_ERROR


def handle_error(exception: Exception, exit_on_error: bool = True) -> int:
    """
    Handle an exception by logging and optionally exiting.

    Parameters:
        exception: The exception to handle.
        exit_on_error: Whether to exit the program (default True).

    Returns:
        int: Exit code that would be used.
    """
    exit_code = get_exit_code(exception)

    logger.error(
        "error_occurred",
        exception_type=type(exception).__name__,
        exception_message=str(exception),
        exit_code=exit_code,
        exc_info=True,
    )

    if exit_on_error:
        sys.exit(exit_code)

    return exit_code


def with_error_handling(func: F) -> F:
    """
    Decorator to add error handling to a function.

    Catches exceptions, logs them, and exits with appropriate code.

    Parameters:
        func: Function to decorate.

    Returns:
        Decorated function with error handling.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ADAAnnotatorError as e:
            handle_error(e, exit_on_error=True)
        except Exception:
            logger.exception("unexpected_error", exc_info=True)
            sys.exit(EXIT_GENERAL_ERROR)

    return cast(F, wrapper)
