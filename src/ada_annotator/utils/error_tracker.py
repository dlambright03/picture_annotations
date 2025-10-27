"""
Error tracking utility for ADA Annotator.

Tracks processing failures with categorization and detailed
error information for reporting.
"""

from enum import Enum
from typing import Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class ErrorCategory(str, Enum):
    """
    Category of processing error.

    Used to classify errors for reporting and analysis.
    """

    API = "API"
    VALIDATION = "VALIDATION"
    FILE = "FILE"
    PROCESSING = "PROCESSING"
    UNKNOWN = "UNKNOWN"


class ErrorTracker:
    """
    Track processing failures during document processing.

    Maintains a list of all failures with:
    - Image ID and location information
    - Error type and category
    - Detailed error message
    - All errors are also logged
    """

    def __init__(self) -> None:
        """Initialize error tracker."""
        self._errors: List[Dict[str, str]] = []

    def track_error(
        self,
        image_id: str,
        error_message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        page: Optional[str] = None,
        location: Optional[str] = None,
    ) -> None:
        """
        Track a processing error for an image.

        Args:
            image_id: Unique identifier for the image.
            error_message: Description of the error.
            category: Category of error (API, validation, etc.).
            page: Page or slide number where image is located.
            location: Additional location info (paragraph, shape).
        """
        error_entry = {
            "image_id": image_id,
            "error_message": error_message,
            "category": category.value,
        }

        if page is not None:
            error_entry["page"] = str(page)

        if location is not None:
            error_entry["location"] = location

        self._errors.append(error_entry)

        # Also log the error
        logger.error(
            "image_processing_failed",
            image_id=image_id,
            error_message=error_message,
            category=category.value,
            page=page,
            location=location,
        )

    def get_errors(self) -> List[Dict[str, str]]:
        """
        Get all tracked errors.

        Returns:
            List of error dictionaries.
        """
        return self._errors.copy()

    def get_error_count(self) -> int:
        """
        Get total number of tracked errors.

        Returns:
            Count of errors.
        """
        return len(self._errors)

    def get_errors_by_category(
        self,
        category: ErrorCategory
    ) -> List[Dict[str, str]]:
        """
        Get errors filtered by category.

        Args:
            category: Error category to filter by.

        Returns:
            List of errors matching the category.
        """
        return [
            error for error in self._errors
            if error.get("category") == category.value
        ]

    def get_category_counts(self) -> Dict[str, int]:
        """
        Get count of errors by category.

        Returns:
            Dictionary mapping category names to counts.
        """
        counts: Dict[str, int] = {}

        for error in self._errors:
            category = error.get("category", ErrorCategory.UNKNOWN.value)
            counts[category] = counts.get(category, 0) + 1

        return counts

    def has_errors(self) -> bool:
        """
        Check if any errors have been tracked.

        Returns:
            True if errors exist, False otherwise.
        """
        return len(self._errors) > 0

    def clear(self) -> None:
        """Clear all tracked errors."""
        self._errors.clear()
