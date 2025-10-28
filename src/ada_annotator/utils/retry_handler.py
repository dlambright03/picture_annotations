"""
Retry handler with exponential backoff for API calls.

Provides retry logic for handling transient API failures.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar

from ada_annotator.exceptions import APIError
from ada_annotator.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
    """

    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given retry attempt using exponential backoff.

        Args:
            attempt: Current retry attempt number (0-indexed)

        Returns:
            Delay in seconds (capped at max_delay)

        Example:
            >>> config = RetryConfig(initial_delay=1.0, exponential_base=2.0)
            >>> config.get_delay(0)  # 1.0
            >>> config.get_delay(1)  # 2.0
            >>> config.get_delay(2)  # 4.0
        """
        delay = self.initial_delay * (self.exponential_base**attempt)
        return min(delay, self.max_delay)


def should_retry_error(error: Exception) -> bool:
    """
    Determine if an error should trigger a retry attempt.

    Args:
        error: Exception that was raised

    Returns:
        True if error is retryable, False otherwise

    Retryable errors:
        - 429: Rate limit exceeded
        - 503: Service unavailable
        - 504: Gateway timeout

    Non-retryable errors:
        - 400: Bad request
        - 401: Unauthorized
        - 404: Not found
        - Other exceptions
    """
    if not isinstance(error, APIError):
        return False

    if error.status_code is None:
        return False

    # Retry on transient server errors and rate limits
    retryable_codes = {429, 503, 504}
    return error.status_code in retryable_codes


def retry_with_exponential_backoff(
    config: RetryConfig | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that adds retry logic with exponential backoff.

    Args:
        config: Retry configuration (uses defaults if None)

    Returns:
        Decorated function with retry logic

    Example:
        >>> @retry_with_exponential_backoff()
        ... def call_api():
        ...     # May raise APIError with status_code=429
        ...     return api_client.get_data()

        >>> @retry_with_exponential_backoff(
        ...     config=RetryConfig(max_retries=5, initial_delay=2.0)
        ... )
        ... def important_api_call():
        ...     return critical_api.process()
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if we should retry
                    if not should_retry_error(e):
                        # Non-retryable error, raise immediately
                        raise

                    # Check if we've exhausted retries
                    if attempt >= config.max_retries:
                        logger.error(
                            f"Max retries ({config.max_retries}) exceeded for "
                            f"{func.__name__}: {e}"
                        )
                        raise

                    # Calculate delay and wait
                    delay = config.get_delay(attempt)
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_retries} for "
                        f"{func.__name__} after {delay}s delay. Error: {e}"
                    )
                    time.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry loop termination")

        return wrapper

    return decorator
