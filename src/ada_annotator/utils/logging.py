"""
Structured logging configuration using structlog.

This module provides JSON-formatted logging with correlation IDs for
production-ready observability and debugging capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.processors import JSONRenderer
from structlog.stdlib import add_log_level, add_logger_name


def setup_logging(
    log_file: Path,
    log_level: str = "INFO",
    enable_console: bool = True
) -> None:
    """
    Configure structured JSON logging with file and console handlers.
    
    Parameters:
        log_file (Path): Path to the log file.
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR,
                        CRITICAL).
        enable_console (bool): Whether to enable console logging.
    
    Returns:
        None
    
    Raises:
        ValueError: If log_level is invalid.
        OSError: If log file cannot be created.
    """
    # Validate log level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog processors
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            add_logger_name,
            add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Add file handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    except OSError as e:
        raise OSError(f"Cannot create log file {log_file}: {e}") from e
    
    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        console_handler.setLevel(numeric_level)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Parameters:
        name (str): Logger name (typically __name__).
    
    Returns:
        structlog.BoundLogger: Configured logger instance.
    """
    return structlog.get_logger(name)


def add_correlation_id(
    logger: structlog.BoundLogger,
    correlation_id: str
) -> structlog.BoundLogger:
    """
    Add correlation ID to logger context.
    
    Parameters:
        logger (structlog.BoundLogger): Logger instance.
        correlation_id (str): Unique correlation ID for request tracing.
    
    Returns:
        structlog.BoundLogger: Logger with correlation ID bound.
    """
    return logger.bind(correlation_id=correlation_id)
