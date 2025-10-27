"""
Custom exceptions for ADA Annotator.

Defines the exception hierarchy for the application.
"""

from typing import Optional


class ADAAnnotatorError(Exception):
    """
    Base exception for all ADA Annotator errors.

    All custom exceptions inherit from this base class.
    """

    pass


class FileError(ADAAnnotatorError):
    """
    Raised when file operations fail.

    Examples:
        - File not found
        - File not readable
        - File format not supported
        - File corrupted
    """

    pass


class APIError(ADAAnnotatorError):
    """
    Raised when API calls fail.

    Examples:
        - API timeout
        - API rate limit exceeded
        - API authentication failure
        - Invalid API response

    Attributes:
        message: Error message
        status_code: HTTP status code (optional)
    """

    def __init__(self, message: str, status_code: Optional[int] = None):
        """
        Initialize API error with message and optional status code.

        Args:
            message: Error description
            status_code: HTTP status code if applicable
        """
        super().__init__(message)
        self.status_code = status_code



class ValidationError(ADAAnnotatorError):
    """
    Raised when validation fails.

    Examples:
        - Alt-text exceeds character limit
        - Alt-text contains prohibited content
        - Configuration validation failure
        - Data model validation failure
    """

    pass


class ProcessingError(ADAAnnotatorError):
    """
    Raised when document processing fails.

    Examples:
        - Image extraction failure
        - Context extraction failure
        - Alt-text injection failure
        - Document save failure
    """

    pass


# Exit codes for CLI
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_INPUT_ERROR = 2
EXIT_API_ERROR = 3
EXIT_VALIDATION_ERROR = 4
