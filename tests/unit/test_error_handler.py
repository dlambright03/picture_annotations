"""
Unit tests for error handling utilities.
"""

import pytest

from ada_annotator.exceptions import (
    APIError,
    EXIT_API_ERROR,
    EXIT_GENERAL_ERROR,
    EXIT_INPUT_ERROR,
    EXIT_SUCCESS,
    EXIT_VALIDATION_ERROR,
    FileError,
    ProcessingError,
    ValidationError,
)
from ada_annotator.utils.error_handler import (
    get_exit_code,
    handle_error,
)


class TestExceptions:
    """Tests for custom exceptions."""

    def test_file_error_inheritance(self):
        """Test FileError inherits from ADAAnnotatorError."""
        error = FileError("File not found")
        assert str(error) == "File not found"

    def test_api_error_inheritance(self):
        """Test APIError inherits from ADAAnnotatorError."""
        error = APIError("API timeout")
        assert str(error) == "API timeout"

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from ADAAnnotatorError."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"

    def test_processing_error_inheritance(self):
        """Test ProcessingError inherits from ADAAnnotatorError."""
        error = ProcessingError("Processing failed")
        assert str(error) == "Processing failed"


class TestErrorHandler:
    """Tests for error handler utilities."""

    def test_get_exit_code_file_error(self):
        """Test exit code for FileError."""
        error = FileError("Test")
        assert get_exit_code(error) == EXIT_INPUT_ERROR

    def test_get_exit_code_api_error(self):
        """Test exit code for APIError."""
        error = APIError("Test")
        assert get_exit_code(error) == EXIT_API_ERROR

    def test_get_exit_code_validation_error(self):
        """Test exit code for ValidationError."""
        error = ValidationError("Test")
        assert get_exit_code(error) == EXIT_VALIDATION_ERROR

    def test_get_exit_code_processing_error(self):
        """Test exit code for ProcessingError."""
        error = ProcessingError("Test")
        assert get_exit_code(error) == EXIT_GENERAL_ERROR

    def test_get_exit_code_generic_error(self):
        """Test exit code for generic Exception."""
        error = Exception("Test")
        assert get_exit_code(error) == EXIT_GENERAL_ERROR

    def test_get_exit_code_file_not_found_error(self):
        """Test exit code for FileNotFoundError."""
        error = FileNotFoundError("File not found")
        assert get_exit_code(error) == EXIT_INPUT_ERROR

    def test_get_exit_code_value_error(self):
        """Test exit code for ValueError."""
        error = ValueError("Invalid value")
        assert get_exit_code(error) == EXIT_INPUT_ERROR

    def test_get_exit_code_permission_error(self):
        """Test exit code for PermissionError."""
        error = PermissionError("Permission denied")
        assert get_exit_code(error) == EXIT_INPUT_ERROR

    def test_handle_error_without_exit(self):
        """Test handle_error with exit_on_error=False."""
        error = FileError("Test error")
        exit_code = handle_error(error, exit_on_error=False)

        assert exit_code == EXIT_INPUT_ERROR

    def test_handle_error_with_exit(self):
        """Test handle_error calls sys.exit."""
        error = APIError("Test error")

        with pytest.raises(SystemExit) as exc_info:
            handle_error(error, exit_on_error=True)

        assert exc_info.value.code == EXIT_API_ERROR
