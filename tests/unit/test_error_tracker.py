"""
Tests for error tracker module.

Tests error tracking, categorization, and reporting functionality.
"""

import pytest

from ada_annotator.utils import ErrorCategory, ErrorTracker


@pytest.fixture
def error_tracker() -> ErrorTracker:
    """Create error tracker instance."""
    return ErrorTracker()


def test_error_tracker_initialization(error_tracker):
    """Test error tracker initialization."""
    assert error_tracker is not None
    assert error_tracker.get_error_count() == 0
    assert not error_tracker.has_errors()


def test_track_error_basic(error_tracker):
    """Test basic error tracking."""
    error_tracker.track_error(
        image_id="img-001",
        error_message="Test error message",
        category=ErrorCategory.API,
    )

    assert error_tracker.get_error_count() == 1
    assert error_tracker.has_errors()

    errors = error_tracker.get_errors()
    assert len(errors) == 1
    assert errors[0]["image_id"] == "img-001"
    assert errors[0]["error_message"] == "Test error message"
    assert errors[0]["category"] == "API"


def test_track_error_with_page(error_tracker):
    """Test error tracking with page number."""
    error_tracker.track_error(
        image_id="img-002",
        error_message="Page-specific error",
        category=ErrorCategory.VALIDATION,
        page="5",
    )

    errors = error_tracker.get_errors()
    assert errors[0]["page"] == "5"


def test_track_error_with_location(error_tracker):
    """Test error tracking with location information."""
    error_tracker.track_error(
        image_id="img-003",
        error_message="Location-specific error",
        category=ErrorCategory.FILE,
        location="paragraph 12",
    )

    errors = error_tracker.get_errors()
    assert errors[0]["location"] == "paragraph 12"


def test_track_error_with_all_fields(error_tracker):
    """Test error tracking with all optional fields."""
    error_tracker.track_error(
        image_id="img-004",
        error_message="Complete error",
        category=ErrorCategory.PROCESSING,
        page="3",
        location="slide 5, shape 2",
    )

    errors = error_tracker.get_errors()
    error = errors[0]

    assert error["image_id"] == "img-004"
    assert error["error_message"] == "Complete error"
    assert error["category"] == "PROCESSING"
    assert error["page"] == "3"
    assert error["location"] == "slide 5, shape 2"


def test_track_multiple_errors(error_tracker):
    """Test tracking multiple errors."""
    error_tracker.track_error(
        "img-001", "Error 1", ErrorCategory.API
    )
    error_tracker.track_error(
        "img-002", "Error 2", ErrorCategory.VALIDATION
    )
    error_tracker.track_error(
        "img-003", "Error 3", ErrorCategory.FILE
    )

    assert error_tracker.get_error_count() == 3
    errors = error_tracker.get_errors()
    assert len(errors) == 3


def test_get_errors_by_category(error_tracker):
    """Test filtering errors by category."""
    error_tracker.track_error(
        "img-001", "API Error 1", ErrorCategory.API
    )
    error_tracker.track_error(
        "img-002", "API Error 2", ErrorCategory.API
    )
    error_tracker.track_error(
        "img-003", "Validation Error", ErrorCategory.VALIDATION
    )
    error_tracker.track_error(
        "img-004", "File Error", ErrorCategory.FILE
    )

    api_errors = error_tracker.get_errors_by_category(ErrorCategory.API)
    assert len(api_errors) == 2
    assert all(e["category"] == "API" for e in api_errors)

    validation_errors = error_tracker.get_errors_by_category(
        ErrorCategory.VALIDATION
    )
    assert len(validation_errors) == 1


def test_get_category_counts(error_tracker):
    """Test getting error counts by category."""
    error_tracker.track_error(
        "img-001", "Error 1", ErrorCategory.API
    )
    error_tracker.track_error(
        "img-002", "Error 2", ErrorCategory.API
    )
    error_tracker.track_error(
        "img-003", "Error 3", ErrorCategory.API
    )
    error_tracker.track_error(
        "img-004", "Error 4", ErrorCategory.VALIDATION
    )
    error_tracker.track_error(
        "img-005", "Error 5", ErrorCategory.VALIDATION
    )
    error_tracker.track_error(
        "img-006", "Error 6", ErrorCategory.FILE
    )

    counts = error_tracker.get_category_counts()

    assert counts["API"] == 3
    assert counts["VALIDATION"] == 2
    assert counts["FILE"] == 1


def test_error_category_enum():
    """Test ErrorCategory enum values."""
    assert ErrorCategory.API.value == "API"
    assert ErrorCategory.VALIDATION.value == "VALIDATION"
    assert ErrorCategory.FILE.value == "FILE"
    assert ErrorCategory.PROCESSING.value == "PROCESSING"
    assert ErrorCategory.UNKNOWN.value == "UNKNOWN"


def test_track_error_default_category(error_tracker):
    """Test tracking error with default UNKNOWN category."""
    error_tracker.track_error(
        image_id="img-999",
        error_message="Unknown error type",
    )

    errors = error_tracker.get_errors()
    assert errors[0]["category"] == "UNKNOWN"


def test_clear_errors(error_tracker):
    """Test clearing all errors."""
    error_tracker.track_error(
        "img-001", "Error 1", ErrorCategory.API
    )
    error_tracker.track_error(
        "img-002", "Error 2", ErrorCategory.VALIDATION
    )

    assert error_tracker.get_error_count() == 2

    error_tracker.clear()

    assert error_tracker.get_error_count() == 0
    assert not error_tracker.has_errors()


def test_get_errors_returns_copy(error_tracker):
    """Test that get_errors returns a copy, not reference."""
    error_tracker.track_error(
        "img-001", "Error 1", ErrorCategory.API
    )

    errors1 = error_tracker.get_errors()
    errors2 = error_tracker.get_errors()

    # Should be different objects
    assert errors1 is not errors2
    # But with same content
    assert errors1 == errors2


def test_has_errors_false_initially(error_tracker):
    """Test has_errors returns False for new tracker."""
    assert not error_tracker.has_errors()


def test_has_errors_true_after_tracking(error_tracker):
    """Test has_errors returns True after tracking error."""
    error_tracker.track_error(
        "img-001", "Error", ErrorCategory.API
    )
    assert error_tracker.has_errors()


def test_has_errors_false_after_clear(error_tracker):
    """Test has_errors returns False after clearing."""
    error_tracker.track_error(
        "img-001", "Error", ErrorCategory.API
    )
    error_tracker.clear()
    assert not error_tracker.has_errors()


def test_error_with_numeric_page(error_tracker):
    """Test error tracking converts numeric page to string."""
    error_tracker.track_error(
        image_id="img-007",
        error_message="Numeric page error",
        category=ErrorCategory.FILE,
        page=42,  # type: ignore
    )

    errors = error_tracker.get_errors()
    assert errors[0]["page"] == "42"
    assert isinstance(errors[0]["page"], str)


def test_multiple_categories_tracked(error_tracker):
    """Test tracking errors across all categories."""
    categories = [
        ErrorCategory.API,
        ErrorCategory.VALIDATION,
        ErrorCategory.FILE,
        ErrorCategory.PROCESSING,
        ErrorCategory.UNKNOWN,
    ]

    for i, category in enumerate(categories):
        error_tracker.track_error(
            f"img-{i:03d}",
            f"Error for {category.value}",
            category,
        )

    assert error_tracker.get_error_count() == len(categories)

    counts = error_tracker.get_category_counts()
    for category in categories:
        assert counts[category.value] == 1
