"""Utility modules for ADA Annotator."""

from ada_annotator.utils.context_extractor import ContextExtractor
from ada_annotator.utils.error_handler import (
    get_exit_code,
    handle_error,
    with_error_handling,
)
from ada_annotator.utils.image_utils import (
    convert_image_to_base64,
    get_image_format,
    validate_image_file,
)
from ada_annotator.utils.logging import (
    add_correlation_id,
    get_logger,
    setup_logging,
)
from ada_annotator.utils.retry_handler import (
    RetryConfig,
    retry_with_exponential_backoff,
    should_retry_error,
)

__all__ = [
    "ContextExtractor",
    "get_exit_code",
    "handle_error",
    "with_error_handling",
    "convert_image_to_base64",
    "get_image_format",
    "validate_image_file",
    "add_correlation_id",
    "get_logger",
    "setup_logging",
    "RetryConfig",
    "retry_with_exponential_backoff",
    "should_retry_error",
]
