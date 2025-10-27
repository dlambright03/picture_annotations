"""
Tests for PPTX document assembler.

Validates alt-text application, position preservation, and error
handling for PowerPoint presentations.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from ada_annotator.document_processors.pptx_assembler import (
    PPTXAssembler
)
from ada_annotator.exceptions import ProcessingError
from ada_annotator.models import AltTextResult


class TestPPTXAssemblerInit:
    """Test PPTXAssembler initialization."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_init_valid_pptx(self, mock_pres, tmp_path):
        """Test initialization with valid PPTX file."""
        # Create test file
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        # Mock presentation
        mock_pres.return_value.slides = [Mock(), Mock()]

        # Initialize
        assembler = PPTXAssembler(input_path, output_path)

        assert assembler.input_path == input_path
        assert assembler.output_path == output_path
        assert assembler.presentation is not None
        mock_pres.assert_called_once_with(str(input_path))

    def test_init_missing_file(self, tmp_path):
        """Test initialization with missing file."""
        input_path = tmp_path / "nonexistent.pptx"
        output_path = tmp_path / "output.pptx"

        with pytest.raises(FileNotFoundError):
            PPTXAssembler(input_path, output_path)

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_init_invalid_extension(self, mock_pres, tmp_path):
        """Test initialization with non-PPTX file."""
        input_path = tmp_path / "test.docx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        with pytest.raises(ValueError, match="Not a PPTX file"):
            PPTXAssembler(input_path, output_path)

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_init_corrupted_pptx(self, mock_pres, tmp_path):
        """Test initialization with corrupted PPTX."""
        input_path = tmp_path / "corrupted.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.side_effect = Exception("Corrupted file")

        with pytest.raises(
            ProcessingError,
            match="Failed to load PPTX presentation"
        ):
            PPTXAssembler(input_path, output_path)

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_init_creates_output_directory(self, mock_pres, tmp_path):
        """Test that output directory is created."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "subdir" / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        assert output_path.parent.exists()
        assert assembler.output_path == output_path


class TestPPTXAssemblerAltTextApplication:
    """Test alt-text application methods."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_success(self, mock_pres, tmp_path):
        """Test successful alt-text application."""
        # Setup
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        # Mock slide with picture shape
        mock_shape = Mock()
        mock_shape.shape_type = 13  # MSO_SHAPE_TYPE.PICTURE
        mock_shape.name = "Picture 1"
        mock_shape._element = Mock()
        mock_nv_pr = Mock()
        mock_shape._element.find.return_value = mock_nv_pr

        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        # Create alt-text result
        result = AltTextResult(
            image_id="slide0_shape0",
            alt_text="Test image description.",
            confidence_score=0.9,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=100,
            processing_time_seconds=1.5,
        )

        # Apply alt-text
        status_map = assembler.apply_alt_text([result])

        assert status_map["slide0_shape0"] == "success"
        assert mock_shape.name == "Test image description."
        mock_nv_pr.set.assert_any_call('title', "Test image description.")
        mock_nv_pr.set.assert_any_call('descr', "Test image description.")

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_invalid_image_id(self, mock_pres, tmp_path):
        """Test alt-text application with invalid image_id."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        result = AltTextResult(
            image_id="invalid_format",
            alt_text="Test.",
            confidence_score=0.9,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=50,
            processing_time_seconds=1.0,
        )

        status_map = assembler.apply_alt_text([result])

        assert "failed: invalid image_id format" in status_map["invalid_format"]

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_slide_out_of_range(
        self, mock_pres, tmp_path
    ):
        """Test alt-text application with invalid slide index."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        result = AltTextResult(
            image_id="slide10_shape0",
            alt_text="Test.",
            confidence_score=0.9,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=50,
            processing_time_seconds=1.0,
        )

        status_map = assembler.apply_alt_text([result])

        assert "failed: slide index out of range" in status_map["slide10_shape0"]

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_shape_not_found(self, mock_pres, tmp_path):
        """Test alt-text application when shape not found."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        # Mock slide with no picture shapes
        mock_slide = Mock()
        mock_slide.shapes = []

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        result = AltTextResult(
            image_id="slide0_shape0",
            alt_text="Test.",
            confidence_score=0.9,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=50,
            processing_time_seconds=1.0,
        )

        status_map = assembler.apply_alt_text([result])

        assert "failed: picture shape not found" in status_map["slide0_shape0"]

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_multiple_results(self, mock_pres, tmp_path):
        """Test applying alt-text to multiple images."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        # Mock slides with picture shapes
        mock_shape1 = Mock()
        mock_shape1.shape_type = 13
        mock_shape1._element = Mock()
        mock_shape1._element.find.return_value = Mock()

        mock_shape2 = Mock()
        mock_shape2.shape_type = 13
        mock_shape2._element = Mock()
        mock_shape2._element.find.return_value = Mock()

        mock_slide1 = Mock()
        mock_slide1.shapes = [mock_shape1]

        mock_slide2 = Mock()
        mock_slide2.shapes = [mock_shape2]

        mock_pres.return_value.slides = [mock_slide1, mock_slide2]

        assembler = PPTXAssembler(input_path, output_path)

        results = [
            AltTextResult(
                image_id="slide0_shape0",
                alt_text="First image.",
                confidence_score=0.9,
                validation_passed=True,
                validation_warnings=[],
                tokens_used=50,
                processing_time_seconds=1.0,
            ),
            AltTextResult(
                image_id="slide1_shape0",
                alt_text="Second image.",
                confidence_score=0.85,
                validation_passed=True,
                validation_warnings=[],
                tokens_used=60,
                processing_time_seconds=1.2,
            ),
        ]

        status_map = assembler.apply_alt_text(results)

        assert status_map["slide0_shape0"] == "success"
        assert status_map["slide1_shape0"] == "success"
        assert mock_shape1.name == "First image."
        assert mock_shape2.name == "Second image."


class TestPPTXAssemblerFindPictureShape:
    """Test shape finding methods."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_find_picture_shape_first(self, mock_pres, tmp_path):
        """Test finding first picture shape on slide."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_shape = Mock()
        mock_shape.shape_type = 13  # PICTURE

        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        found_shape = assembler._find_picture_shape(mock_slide, 0, 0)

        assert found_shape == mock_shape

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_find_picture_shape_second(self, mock_pres, tmp_path):
        """Test finding second picture shape on slide."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_shape1 = Mock()
        mock_shape1.shape_type = 13  # PICTURE

        mock_shape2 = Mock()
        mock_shape2.shape_type = 13  # PICTURE

        mock_slide = Mock()
        mock_slide.shapes = [mock_shape1, mock_shape2]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        found_shape = assembler._find_picture_shape(mock_slide, 0, 1)

        assert found_shape == mock_shape2

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_find_picture_shape_skips_non_pictures(
        self, mock_pres, tmp_path
    ):
        """Test that non-picture shapes are skipped."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_text_shape = Mock()
        mock_text_shape.shape_type = 1  # TEXT_BOX

        mock_picture = Mock()
        mock_picture.shape_type = 13  # PICTURE

        mock_slide = Mock()
        mock_slide.shapes = [mock_text_shape, mock_picture]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        found_shape = assembler._find_picture_shape(mock_slide, 0, 0)

        assert found_shape == mock_picture


class TestPPTXAssemblerSaveDocument:
    """Test document saving methods."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_save_document_success(self, mock_pres, tmp_path):
        """Test successful document save."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_presentation = Mock()
        mock_presentation.slides = [Mock()]
        mock_pres.return_value = mock_presentation

        assembler = PPTXAssembler(input_path, output_path)

        # Create dummy output file for stat check
        output_path.touch()

        assembler.save_document()

        mock_presentation.save.assert_called_once_with(str(output_path))

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_save_document_failure(self, mock_pres, tmp_path):
        """Test document save failure."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_presentation = Mock()
        mock_presentation.slides = [Mock()]
        mock_presentation.save.side_effect = Exception("Save failed")
        mock_pres.return_value = mock_presentation

        assembler = PPTXAssembler(input_path, output_path)

        with pytest.raises(
            ProcessingError,
            match="Failed to save PPTX presentation"
        ):
            assembler.save_document()


class TestPPTXAssemblerValidation:
    """Test document validation methods."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_validate_document_valid(self, mock_pres, tmp_path):
        """Test validation of valid document."""
        input_path = tmp_path / "test.pptx"
        input_path.write_bytes(b"fake pptx content")  # Non-empty file
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        assert assembler.validate_document() is True

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_validate_document_no_slides(self, mock_pres, tmp_path):
        """Test validation of document with no slides."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = []

        assembler = PPTXAssembler(input_path, output_path)

        assert assembler.validate_document() is False

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_get_document_format(self, mock_pres, tmp_path):
        """Test get_document_format returns PPTX."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        assert assembler.get_document_format() == "PPTX"


class TestPPTXAssemblerIntegration:
    """Integration tests for PPTX assembler."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_full_workflow(self, mock_pres, tmp_path):
        """Test complete workflow: init  apply  save."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        # Mock presentation with picture shape
        mock_shape = Mock()
        mock_shape.shape_type = 13
        mock_shape._element = Mock()
        mock_shape._element.find.return_value = Mock()

        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]

        mock_presentation = Mock()
        mock_presentation.slides = [mock_slide]
        mock_pres.return_value = mock_presentation

        # Initialize
        assembler = PPTXAssembler(input_path, output_path)

        # Apply alt-text
        result = AltTextResult(
            image_id="slide0_shape0",
            alt_text="Integration test image.",
            confidence_score=0.95,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=80,
            processing_time_seconds=1.8,
        )

        status_map = assembler.apply_alt_text([result])

        assert status_map["slide0_shape0"] == "success"

        # Save
        output_path.touch()  # Create dummy file for stat check
        assembler.save_document()

        mock_presentation.save.assert_called_once_with(str(output_path))

