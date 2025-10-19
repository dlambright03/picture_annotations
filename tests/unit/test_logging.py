"""
Unit tests for logging utilities.
"""

import tempfile
from pathlib import Path

import pytest
import structlog

from ada_annotator.utils.logging import (
    add_correlation_id,
    get_logger,
    setup_logging,
)


class TestLogging:
    """Tests for logging utilities."""

    def test_setup_logging_with_file(self, tmp_path):
        """Test setting up logging with file handler."""
        log_file = tmp_path / "test.log"

        setup_logging(
            log_file=log_file,
            log_level="INFO",
            enable_console=False,
        )

        logger = get_logger("test")
        logger.info("test_message", key="value")

        # Verify log file was created
        assert log_file.exists()

        # Verify log content
        log_content = log_file.read_text()
        assert "test_message" in log_content
        assert '"key": "value"' in log_content

    def test_setup_logging_invalid_level(self, tmp_path):
        """Test that invalid log level raises error."""
        log_file = tmp_path / "test.log"

        with pytest.raises(ValueError, match="Invalid log level"):
            setup_logging(
                log_file=log_file,
                log_level="INVALID",
                enable_console=True,
            )

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")

        assert logger is not None
        # Logger can be BoundLogger or BoundLoggerLazyProxy
        assert hasattr(logger, 'info')

    def test_add_correlation_id(self):
        """Test adding correlation ID to logger."""
        logger = get_logger("test")
        logger_with_id = add_correlation_id(logger, "test-123")

        # Both should have logging capabilities
        assert hasattr(logger, 'info')
        assert hasattr(logger_with_id, 'info')

    def test_logging_levels(self, tmp_path):
        """Test different logging levels."""
        log_file = tmp_path / "test.log"

        # Set to WARNING level
        setup_logging(
            log_file=log_file,
            log_level="WARNING",
            enable_console=False,
        )

        logger = get_logger("test")
        logger.info("info_message")  # Should not appear
        logger.warning("warning_message")  # Should appear
        logger.error("error_message")  # Should appear

        log_content = log_file.read_text()

        assert "info_message" not in log_content
        assert "warning_message" in log_content
        assert "error_message" in log_content
