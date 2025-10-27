"""
Unit tests for retry handler functionality.

Tests exponential backoff and retry logic for API calls.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from ada_annotator.exceptions import APIError
from ada_annotator.utils.retry_handler import (
    RetryConfig,
    retry_with_exponential_backoff,
    should_retry_error,
)


class TestRetryConfig:
    """Test suite for RetryConfig dataclass."""

    def test_creates_with_defaults(self):
        """Should create config with default values."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0

    def test_creates_with_custom_values(self):
        """Should create config with custom values."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
        )

        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0

    def test_calculates_delay_correctly(self):
        """Should calculate exponential backoff delays."""
        config = RetryConfig(initial_delay=1.0, exponential_base=2.0, max_delay=60.0)

        # First retry: 1 * 2^0 = 1
        assert config.get_delay(0) == 1.0
        # Second retry: 1 * 2^1 = 2
        assert config.get_delay(1) == 2.0
        # Third retry: 1 * 2^2 = 4
        assert config.get_delay(2) == 4.0
        # Fourth retry: 1 * 2^3 = 8
        assert config.get_delay(3) == 8.0

    def test_caps_delay_at_max_delay(self):
        """Should not exceed max_delay."""
        config = RetryConfig(initial_delay=10.0, exponential_base=10.0, max_delay=50.0)

        # 10 * 10^5 would be 1,000,000 but should cap at 50
        assert config.get_delay(5) == 50.0


class TestShouldRetryError:
    """Test suite for should_retry_error function."""

    def test_retries_rate_limit_errors(self):
        """Should retry on 429 rate limit errors."""
        error = APIError("Rate limit exceeded", status_code=429)
        assert should_retry_error(error) is True

    def test_retries_service_unavailable_errors(self):
        """Should retry on 503 service unavailable errors."""
        error = APIError("Service unavailable", status_code=503)
        assert should_retry_error(error) is True

    def test_retries_timeout_errors(self):
        """Should retry on 504 gateway timeout errors."""
        error = APIError("Gateway timeout", status_code=504)
        assert should_retry_error(error) is True

    def test_does_not_retry_client_errors(self):
        """Should not retry on 400 bad request errors."""
        error = APIError("Bad request", status_code=400)
        assert should_retry_error(error) is False

    def test_does_not_retry_auth_errors(self):
        """Should not retry on 401 unauthorized errors."""
        error = APIError("Unauthorized", status_code=401)
        assert should_retry_error(error) is False

    def test_does_not_retry_not_found_errors(self):
        """Should not retry on 404 not found errors."""
        error = APIError("Not found", status_code=404)
        assert should_retry_error(error) is False

    def test_does_not_retry_non_api_errors(self):
        """Should not retry non-APIError exceptions."""
        error = ValueError("Some other error")
        assert should_retry_error(error) is False


class TestRetryWithExponentialBackoff:
    """Test suite for retry_with_exponential_backoff decorator."""

    def test_succeeds_on_first_attempt(self):
        """Should return result immediately if no error."""
        @retry_with_exponential_backoff()
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_retries_and_succeeds(self):
        """Should retry on rate limit and eventually succeed."""
        call_count = 0

        @retry_with_exponential_backoff(config=RetryConfig(max_retries=3))
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise APIError("Rate limit", status_code=429)
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    @patch("time.sleep")
    def test_waits_with_exponential_backoff(self, mock_sleep):
        """Should wait with increasing delays between retries."""
        call_count = 0

        @retry_with_exponential_backoff(
            config=RetryConfig(max_retries=3, initial_delay=1.0, exponential_base=2.0)
        )
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise APIError("Service unavailable", status_code=503)
            return "success"

        result = failing_function()

        assert result == "success"
        # Should have slept twice (retry 1 and retry 2)
        assert mock_sleep.call_count == 2
        # First delay: 1.0 second
        assert mock_sleep.call_args_list[0][0][0] == 1.0
        # Second delay: 2.0 seconds
        assert mock_sleep.call_args_list[1][0][0] == 2.0

    def test_gives_up_after_max_retries(self):
        """Should raise error after exhausting all retries."""
        @retry_with_exponential_backoff(config=RetryConfig(max_retries=2))
        def always_fails():
            raise APIError("Rate limit", status_code=429)

        with pytest.raises(APIError, match="Rate limit"):
            always_fails()

    def test_does_not_retry_non_retryable_errors(self):
        """Should immediately raise non-retryable errors."""
        @retry_with_exponential_backoff()
        def bad_request_function():
            raise APIError("Bad request", status_code=400)

        with pytest.raises(APIError, match="Bad request"):
            bad_request_function()

    def test_preserves_function_signature(self):
        """Should preserve original function's signature and docstring."""
        @retry_with_exponential_backoff()
        def documented_function(x: int, y: int) -> int:
            """Add two numbers."""
            return x + y

        assert documented_function(2, 3) == 5
        assert documented_function.__doc__ == "Add two numbers."
        assert documented_function.__name__ == "documented_function"

    def test_works_with_async_functions(self):
        """Should work with async functions (placeholder for future)."""
        # Note: Current implementation is sync-only
        # This test documents expected future behavior
        pass

    @patch("time.sleep")
    def test_logs_retry_attempts(self, mock_sleep):
        """Should log each retry attempt."""
        call_count = 0

        @retry_with_exponential_backoff(config=RetryConfig(max_retries=2))
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APIError("Timeout", status_code=504)
            return "success"

        with patch("ada_annotator.utils.retry_handler.logger") as mock_logger:
            result = flaky_function()

            assert result == "success"
            # Should have logged the retry
            assert mock_logger.warning.called
