"""Tests for CLI utility functions (generate_debug_output_path, process_document_dry_run)."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ada_annotator.cli import generate_debug_output_path, process_document_dry_run


class TestDebugOutputPath:
    """Test generate_debug_output_path utility function."""

    def test_debug_output_path_docx(self):
        """Should generate debug path for DOCX file."""
        input_path = Path("document.docx")
        result = generate_debug_output_path(input_path)

        assert result == Path("document_debug.docx")
        assert result.suffix == ".docx"

    def test_debug_output_path_pptx(self):
        """Should convert PPTX to DOCX debug output."""
        input_path = Path("presentation.pptx")
        result = generate_debug_output_path(input_path)

        assert result == Path("presentation_debug.docx")
        assert result.suffix == ".docx"

    def test_debug_output_path_pdf(self):
        """Should convert PDF to DOCX debug output."""
        input_path = Path("report.pdf")
        result = generate_debug_output_path(input_path)

        assert result == Path("report_debug.docx")
        assert result.suffix == ".docx"


class TestProcessDocumentDryRun:
    """Test process_document_dry_run function."""

    @pytest.fixture
    def mock_logger(self):
        """Provide a mock logger."""
        from unittest.mock import MagicMock
        return MagicMock()

    @pytest.fixture
    def sample_images(self):
        """Provide sample image metadata for testing."""
        from ada_annotator.models import ImageMetadata

        return [
            ImageMetadata(
                image_id="img_001",
                filename="image1.png",
                format="PNG",
                size_bytes=12345,
                width_pixels=800,
                height_pixels=600,
                page_number=1,
                existing_alt_text=None,
                image_data=None,
            ),
            ImageMetadata(
                image_id="img_002",
                filename="image2.jpeg",
                format="JPEG",
                size_bytes=23456,
                width_pixels=1024,
                height_pixels=768,
                page_number=2,
                existing_alt_text=None,
                image_data=None,
            ),
        ]

    @patch('ada_annotator.cli.DOCXExtractor')
    def test_dry_run_docx(self, mock_extractor_class, tmp_path, mock_logger, sample_images):
        """Should perform dry run for DOCX file."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Execute
        result = process_document_dry_run(
            input_path=input_file,
            context_path=None,
            logger=mock_logger,
        )

        # Verify
        assert result.total_images == len(sample_images)
        assert result.document_type == "DOCX"
        mock_extractor_class.assert_called_once_with(input_file)
        mock_extractor.extract_images.assert_called_once()

    @patch('ada_annotator.cli.PPTXExtractor')
    def test_dry_run_pptx(self, mock_extractor_class, tmp_path, mock_logger, sample_images):
        """Should perform dry run for PPTX file."""
        # Setup
        input_file = tmp_path / "test.pptx"
        input_file.write_text("test")

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Execute
        result = process_document_dry_run(
            input_path=input_file,
            context_path=None,
            logger=mock_logger,
        )

        # Verify
        assert result.total_images == len(sample_images)
        assert result.document_type == "PPTX"
        mock_extractor_class.assert_called_once_with(input_file)
        mock_extractor.extract_images.assert_called_once()

    @patch('ada_annotator.cli.PDFExtractor')
    def test_dry_run_pdf(self, mock_extractor_class, tmp_path, mock_logger, sample_images):
        """Should perform dry run for PDF file."""
        # Setup
        input_file = tmp_path / "test.pdf"
        input_file.write_text("test")

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Execute
        result = process_document_dry_run(
            input_path=input_file,
            context_path=None,
            logger=mock_logger,
        )

        # Verify
        assert result.total_images == len(sample_images)
        assert result.document_type == "PDF"
        mock_extractor_class.assert_called_once_with(input_file)
        mock_extractor.extract_images.assert_called_once()

    def test_dry_run_unsupported_format(self, tmp_path, mock_logger):
        """Should raise ValueError for unsupported file format."""
        # Setup
        input_file = tmp_path / "test.xyz"
        input_file.write_text("test")

        # Execute & Verify
        with pytest.raises(ValueError, match="Unsupported format"):
            process_document_dry_run(
                input_path=input_file,
                context_path=None,
                logger=mock_logger,
            )

    @patch('ada_annotator.cli.DOCXExtractor')
    def test_dry_run_no_images(self, mock_extractor_class, tmp_path, mock_logger):
        """Should handle case when no images are found."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")

        # Mock extractor to return empty list
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = []
        mock_extractor_class.return_value = mock_extractor

        # Execute
        result = process_document_dry_run(
            input_path=input_file,
            context_path=None,
            logger=mock_logger,
        )

        # Verify
        assert result.total_images == 0
        assert result.document_type == "DOCX"
        mock_extractor.extract_images.assert_called_once()
