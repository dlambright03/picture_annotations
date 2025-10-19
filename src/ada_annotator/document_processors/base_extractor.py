"""
Base class for document image extractors.

Provides common interface for DOCX and PPTX extractors with shared
functionality for image processing and metadata collection.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import structlog

from ada_annotator.models import ImageMetadata


class DocumentExtractor(ABC):
    """
    Abstract base class for document image extractors.

    Defines common interface for extracting images from different
    document formats (DOCX, PPTX). Subclasses must implement format-
    specific extraction logic.

    Attributes:
        document_path: Path to the document file.
        logger: Structured logger instance.
    """

    def __init__(self, document_path: Path):
        """
        Initialize document extractor.

        Args:
            document_path: Path to document file to process.

        Raises:
            FileNotFoundError: If document does not exist.
            ValueError: If document format is not supported.
        """
        if not document_path.exists():
            raise FileNotFoundError(
                f"Document not found: {document_path}"
            )

        if not document_path.is_file():
            raise ValueError(
                f"Path is not a file: {document_path}"
            )

        self.document_path = document_path
        self.logger = structlog.get_logger(__name__)

        self.logger.info(
            "extractor_initialized",
            document_path=str(document_path),
            file_size_bytes=document_path.stat().st_size,
            extractor_type=self.__class__.__name__,
        )

    @abstractmethod
    def extract_images(self) -> List[ImageMetadata]:
        """
        Extract all images from the document.

        Returns:
            List[ImageMetadata]: List of extracted image metadata.

        Raises:
            ProcessingError: If extraction fails.
        """
        pass

    @abstractmethod
    def get_document_format(self) -> str:
        """
        Get the document format identifier.

        Returns:
            str: Document format (e.g., 'DOCX', 'PPTX').
        """
        pass

    def validate_document(self) -> bool:
        """
        Validate document can be processed.

        Returns:
            bool: True if document is valid, False otherwise.
        """
        # Basic validation - can be overridden by subclasses
        return (
            self.document_path.exists() and
            self.document_path.is_file() and
            self.document_path.stat().st_size > 0
        )
