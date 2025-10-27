"""Utility modules for ADA Annotator."""

from ada_annotator.utils.context_extractor import ContextExtractor
from ada_annotator.utils.error_handler import (
    get_exit_code,
    handle_error,
    with_error_handling,
)
from ada_annotator.utils.logging import (
    add_correlation_id,
    get_logger,
    setup_logging,
)

__all__ = [
    "ContextExtractor",
    "get_exit_code",
    "handle_error",
    "with_error_handling",
    "add_correlation_id",
    "get_logger",
    "setup_logging",
]
