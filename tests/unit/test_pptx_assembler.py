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


class TestPPTXAssemblerDecorativeImages:
    """Test handling of decorative images."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_decorative_alt_text(self, mock_pres, tmp_path):
        """Test applying empty alt-text for decorative images."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_shape = Mock()
        mock_shape.shape_type = 13
        mock_shape._element = Mock()
        mock_shape._element.find.return_value = Mock()

        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        result = AltTextResult(
            image_id="slide0_shape0",
            alt_text="",  # Empty for decorative
            confidence_score=0.95,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=10,
            processing_time_seconds=0.5,
            is_decorative=True,
        )

        status_map = assembler.apply_alt_text([result])

        assert status_map["slide0_shape0"] == "success"
        assert mock_shape.name == ""


class TestPPTXAssemblerSetAltTextMethods:
    """Test _set_alt_text_on_shape method variations."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_set_alt_text_no_element(self, mock_pres, tmp_path):
        """Test setting alt-text on shape without _element."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        # Create shape without _element attribute
        mock_shape = Mock(spec=['name'])
        mock_shape.name = "Old name"

        result = assembler._set_alt_text_on_shape(mock_shape, "New alt-text")

        assert result is True
        assert mock_shape.name == "New alt-text"

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_set_alt_text_xml_error(self, mock_pres, tmp_path):
        """Test handling of XML errors during alt-text setting."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        # Create shape with _element that raises exception
        mock_shape = Mock()
        mock_shape.name = "Shape"
        mock_shape._element.find.side_effect = Exception("XML error")

        result = assembler._set_alt_text_on_shape(mock_shape, "Alt-text")

        # Should still succeed due to name property
        assert result is True

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_set_alt_text_no_cnvpr(self, mock_pres, tmp_path):
        """Test setting alt-text when cNvPr element not found."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        mock_shape = Mock()
        mock_shape.name = "Shape"
        mock_shape._element.find.return_value = None  # No cNvPr found

        result = assembler._set_alt_text_on_shape(mock_shape, "Alt-text")

        assert result is True

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_set_alt_text_with_cnvpr(self, mock_pres, tmp_path):
        """Test setting alt-text with valid cNvPr element."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        mock_cnvpr = Mock()
        mock_shape = Mock()
        mock_shape.name = "Shape"
        mock_shape._element.find.return_value = mock_cnvpr

        result = assembler._set_alt_text_on_shape(mock_shape, "Test alt-text")

        assert result is True
        mock_cnvpr.set.assert_any_call("title", "Test alt-text")
        mock_cnvpr.set.assert_any_call("descr", "Test alt-text")


class TestPPTXAssemblerEdgeCases:
    """Test edge cases and error conditions."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_empty_list(self, mock_pres, tmp_path):
        """Test applying alt-text with empty results list."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        status_map = assembler.apply_alt_text([])

        assert len(status_map) == 0

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_exception_handling(self, mock_pres, tmp_path):
        """Test that exceptions during alt-text application are caught."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_pres.return_value.slides = [Mock()]

        assembler = PPTXAssembler(input_path, output_path)

        # Mock _apply_alt_text_to_image to raise exception
        def raise_error(result):
            raise Exception("Test error")

        assembler._apply_alt_text_to_image = raise_error

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

        assert "failed: Test error" in status_map["slide0_shape0"]

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_with_special_characters(self, mock_pres, tmp_path):
        """Test applying alt-text with special characters."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_shape = Mock()
        mock_shape.shape_type = 13
        mock_shape._element = Mock()
        mock_shape._element.find.return_value = Mock()

        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        special_alt_text = 'Image with "quotes" & <special> chars @#$%'

        result = AltTextResult(
            image_id="slide0_shape0",
            alt_text=special_alt_text,
            confidence_score=0.9,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=50,
            processing_time_seconds=1.0,
        )

        status_map = assembler.apply_alt_text([result])

        assert status_map["slide0_shape0"] == "success"
        assert mock_shape.name == special_alt_text

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_with_unicode(self, mock_pres, tmp_path):
        """Test applying alt-text with unicode characters."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        mock_shape = Mock()
        mock_shape.shape_type = 13
        mock_shape._element = Mock()
        mock_shape._element.find.return_value = Mock()

        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        unicode_text = "Diagram with émojis 🎨 📊 中文 العربية"

        result = AltTextResult(
            image_id="slide0_shape0",
            alt_text=unicode_text,
            confidence_score=0.9,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=50,
            processing_time_seconds=1.0,
        )

        status_map = assembler.apply_alt_text([result])

        assert status_map["slide0_shape0"] == "success"

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_find_picture_shape_mixed_types(self, mock_pres, tmp_path):
        """Test finding picture shape among mixed shape types."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        # Create mixed shapes
        text_shape = Mock()
        text_shape.shape_type = 1  # TEXT_BOX

        picture1 = Mock()
        picture1.shape_type = 13  # PICTURE

        rectangle = Mock()
        rectangle.shape_type = 5  # RECTANGLE

        picture2 = Mock()
        picture2.shape_type = 13  # PICTURE

        mock_slide = Mock()
        mock_slide.shapes = [text_shape, picture1, rectangle, picture2]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        # Find first picture (should be picture1)
        found = assembler._find_picture_shape(mock_slide, 0, 0)
        assert found == picture1

        # Find second picture (should be picture2)
        found = assembler._find_picture_shape(mock_slide, 0, 1)
        assert found == picture2

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_find_picture_shape_index_out_of_range(self, mock_pres, tmp_path):
        """Test finding picture shape with index out of range."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        picture = Mock()
        picture.shape_type = 13

        mock_slide = Mock()
        mock_slide.shapes = [picture]

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        # Try to find shape index 5 when only 1 exists
        found = assembler._find_picture_shape(mock_slide, 0, 5)

        assert found is None


class TestPPTXAssemblerMultipleShapes:
    """Test handling of multiple shapes on slides."""

    @patch('ada_annotator.document_processors.pptx_assembler.Presentation')
    def test_apply_alt_text_to_multiple_shapes_same_slide(
        self, mock_pres, tmp_path
    ):
        """Test applying alt-text to multiple shapes on same slide."""
        input_path = tmp_path / "test.pptx"
        input_path.touch()
        output_path = tmp_path / "output.pptx"

        # Create three picture shapes on one slide
        shapes = []
        for i in range(3):
            shape = Mock()
            shape.shape_type = 13
            shape._element = Mock()
            shape._element.find.return_value = Mock()
            shapes.append(shape)

        mock_slide = Mock()
        mock_slide.shapes = shapes

        mock_pres.return_value.slides = [mock_slide]

        assembler = PPTXAssembler(input_path, output_path)

        results = [
            AltTextResult(
                image_id=f"slide0_shape{i}",
                alt_text=f"Image {i+1}.",
                confidence_score=0.9,
                validation_passed=True,
                validation_warnings=[],
                tokens_used=50,
                processing_time_seconds=1.0,
            )
            for i in range(3)
        ]

        status_map = assembler.apply_alt_text(results)

        assert all(v == "success" for v in status_map.values())
        assert shapes[0].name == "Image 1."
        assert shapes[1].name == "Image 2."
        assert shapes[2].name == "Image 3."

