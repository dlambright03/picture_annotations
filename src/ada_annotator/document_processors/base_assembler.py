"""
Base class for document assemblers.

Provides common interface for DOCX and PPTX assemblers with shared
functionality for applying alt-text to documents and saving output.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

import structlog

from ada_annotator.models import AltTextResult


class DocumentAssembler(ABC):
    """
    Abstract base class for document assemblers.

    Defines common interface for applying alt-text to different
    document formats (DOCX, PPTX). Subclasses must implement format-
    specific assembly logic.

    Attributes:
        input_path: Path to the input document file.
        output_path: Path where output document will be saved.
        logger: Structured logger instance.
    """

    def __init__(self, input_path: Path, output_path: Path):
        """
        Initialize document assembler.

        Args:
            input_path: Path to input document file.
            output_path: Path where output document will be saved.

        Raises:
            FileNotFoundError: If input document does not exist.
            ValueError: If paths are invalid.
        """
        if not input_path.exists():
            raise FileNotFoundError(
                f"Input document not found: {input_path}"
            )

        if not input_path.is_file():
            raise ValueError(
                f"Input path is not a file: {input_path}"
            )

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.input_path = input_path
        self.output_path = output_path
        self.logger = structlog.get_logger(__name__)

        self.logger.info(
            "assembler_initialized",
            input_path=str(input_path),
            output_path=str(output_path),
            file_size_bytes=input_path.stat().st_size,
            assembler_type=self.__class__.__name__,
        )

    @abstractmethod
    def apply_alt_text(
        self,
        alt_text_results: List[AltTextResult]
    ) -> Dict[str, str]:
        """
        Apply alt-text to images in the document.

        Args:
            alt_text_results: List of alt-text generation results.

        Returns:
            Dict[str, str]: Map of image_id to status message.
                Status can be: 'success', 'skipped', 'failed'.

        Raises:
            ProcessingError: If alt-text application fails.
        """
        pass

    @abstractmethod
    def save_document(self) -> None:
        """
        Save the modified document to output path.

        Raises:
            ProcessingError: If save operation fails.
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
        Validate input document can be processed.

        Returns:
            bool: True if document is valid, False otherwise.
        """
        # Basic validation - can be overridden by subclasses
        return (
            self.input_path.exists() and
            self.input_path.is_file() and
            self.input_path.stat().st_size > 0
        )
