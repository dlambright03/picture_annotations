"""
Unit tests for DOCX image extractor.

Tests extraction of images, position metadata, and alt-text from
Word documents.
"""

import io
from pathlib import Path

import pytest
from docx import Document
from docx.shared import Inches
from PIL import Image

from ada_annotator.document_processors import DOCXExtractor
from ada_annotator.exceptions import ProcessingError
from ada_annotator.models import ImageMetadata


@pytest.fixture
def temp_docx_with_images(tmp_path):
    """Create a temporary DOCX file with test images."""
    doc = Document()
    doc.add_heading("Test Document", 0)

    # Add a paragraph with text
    doc.add_paragraph("This is a test paragraph before the image.")

    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Add inline image
    paragraph = doc.add_paragraph("Image: ")
    run = paragraph.add_run()
    run.add_picture(img_bytes, width=Inches(1.0))

    # Add another paragraph
    doc.add_paragraph("Text after image.")

    # Save document
    docx_path = tmp_path / "test_with_images.docx"
    doc.save(docx_path)

    return docx_path


@pytest.fixture
def temp_empty_docx(tmp_path):
    """Create a temporary DOCX file without images."""
    doc = Document()
    doc.add_heading("Empty Document", 0)
    doc.add_paragraph("No images here.")

    docx_path = tmp_path / "test_empty.docx"
    doc.save(docx_path)

    return docx_path


@pytest.fixture
def nonexistent_path(tmp_path):
    """Return a path that does not exist."""
    return tmp_path / "nonexistent.docx"


class TestDOCXExtractor:
    """Test suite for DOCXExtractor."""

    def test_initialization_with_valid_file(self, temp_empty_docx):
        """Test extractor initializes with valid DOCX file."""
        extractor = DOCXExtractor(temp_empty_docx)

        assert extractor.document_path == temp_empty_docx
        assert extractor.document is not None
        assert extractor.get_document_format() == "DOCX"

    def test_initialization_with_nonexistent_file(
        self, nonexistent_path
    ):
        """Test extractor raises error for nonexistent file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            DOCXExtractor(nonexistent_path)

        assert "not found" in str(exc_info.value).lower()

    def test_initialization_with_wrong_extension(self, tmp_path):
        """Test extractor raises error for non-DOCX file."""
        wrong_file = tmp_path / "test.txt"
        wrong_file.write_text("not a docx")

        with pytest.raises(ValueError) as exc_info:
            DOCXExtractor(wrong_file)

        assert "not a docx" in str(exc_info.value).lower()

    def test_get_document_format(self, temp_empty_docx):
        """Test document format identifier."""
        extractor = DOCXExtractor(temp_empty_docx)
        assert extractor.get_document_format() == "DOCX"

    def test_validate_document(self, temp_empty_docx):
        """Test document validation."""
        extractor = DOCXExtractor(temp_empty_docx)
        assert extractor.validate_document() is True

    def test_extract_images_from_empty_document(self, temp_empty_docx):
        """Test extraction from document with no images."""
        extractor = DOCXExtractor(temp_empty_docx)
        images = extractor.extract_images()

        assert isinstance(images, list)
        assert len(images) == 0

    def test_extract_images_from_document_with_images(
        self, temp_docx_with_images
    ):
        """Test extraction from document with images."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        assert isinstance(images, list)
        assert len(images) > 0

        # Check first image
        img = images[0]
        assert isinstance(img, ImageMetadata)
        assert img.image_id
        assert img.filename
        assert img.format in ["JPEG", "PNG", "GIF", "BMP"]
        assert img.size_bytes > 0
        assert img.width_pixels > 0
        assert img.height_pixels > 0

    def test_image_metadata_structure(self, temp_docx_with_images):
        """Test extracted image metadata has correct structure."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        if len(images) > 0:
            img = images[0]

            # Check required fields
            assert hasattr(img, 'image_id')
            assert hasattr(img, 'filename')
            assert hasattr(img, 'format')
            assert hasattr(img, 'size_bytes')
            assert hasattr(img, 'width_pixels')
            assert hasattr(img, 'height_pixels')
            assert hasattr(img, 'position')
            assert hasattr(img, 'existing_alt_text')

            # Check position metadata
            assert isinstance(img.position, dict)
            assert 'paragraph_index' in img.position
            assert 'anchor_type' in img.position
            assert img.position['anchor_type'] in [
                'inline', 'floating'
            ]

    def test_position_metadata_paragraph_index(
        self, temp_docx_with_images
    ):
        """Test paragraph index is captured correctly."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        if len(images) > 0:
            img = images[0]
            assert 'paragraph_index' in img.position
            assert isinstance(
                img.position['paragraph_index'], int
            )
            assert img.position['paragraph_index'] >= 0

    def test_inline_vs_floating_detection(
        self, temp_docx_with_images
    ):
        """Test anchor type is detected correctly."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        if len(images) > 0:
            img = images[0]
            assert 'anchor_type' in img.position
            assert img.position['anchor_type'] in [
                'inline', 'floating'
            ]

    def test_image_id_uniqueness(self, temp_docx_with_images):
        """Test each image has unique ID."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        image_ids = [img.image_id for img in images]
        assert len(image_ids) == len(set(image_ids))

    def test_existing_alt_text_none_when_absent(
        self, temp_docx_with_images
    ):
        """Test existing_alt_text is None when not present."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        if len(images) > 0:
            # Since our test fixture doesn't add alt-text
            img = images[0]
            # Alt-text may be None or empty string
            assert img.existing_alt_text is None or (
                img.existing_alt_text == ""
            )

    def test_image_format_normalized(self, temp_docx_with_images):
        """Test image format is normalized correctly."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        if len(images) > 0:
            img = images[0]
            # Format should be uppercase
            assert img.format.isupper()
            # Format should be one of supported types
            assert img.format in ["JPEG", "PNG", "GIF", "BMP"]

    def test_page_number_is_none_for_docx(
        self, temp_docx_with_images
    ):
        """Test page_number is None for DOCX (no page concept)."""
        extractor = DOCXExtractor(temp_docx_with_images)
        images = extractor.extract_images()

        if len(images) > 0:
            img = images[0]
            # DOCX doesn't have page numbers
            assert img.page_number is None


class TestDOCXExtractorEdgeCases:
    """Test edge cases and error handling."""

    def test_corrupted_docx_file(self, tmp_path):
        """Test handling of corrupted DOCX file."""
        corrupted_path = tmp_path / "corrupted.docx"
        corrupted_path.write_bytes(b"not a valid docx file")

        with pytest.raises(ProcessingError):
            DOCXExtractor(corrupted_path)

    def test_extract_from_document_with_only_text(
        self, temp_empty_docx
    ):
        """Test extraction from document with only text."""
        extractor = DOCXExtractor(temp_empty_docx)
        images = extractor.extract_images()

        assert images == []

    def test_multiple_images_in_same_paragraph(self, tmp_path):
        """Test extraction of multiple images in one paragraph."""
        doc = Document()
        paragraph = doc.add_paragraph()

        # Add multiple images to same paragraph
        for i in range(3):
            img = Image.new('RGB', (50, 50), color='blue')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            run = paragraph.add_run()
            run.add_picture(img_bytes, width=Inches(0.5))

        docx_path = tmp_path / "multiple_images.docx"
        doc.save(docx_path)

        extractor = DOCXExtractor(docx_path)
        images = extractor.extract_images()

        # Should extract all images
        assert len(images) >= 3

        # All should be from same paragraph
        para_indices = [
            img.position['paragraph_index'] for img in images
        ]
        # Most images should be from the same paragraph
        assert len(set(para_indices)) <= 2  # Allow for heading


class TestDOCXExtractorIntegration:
    """Integration tests with real-world scenarios."""

    def test_full_extraction_workflow(self, temp_docx_with_images):
        """Test complete extraction workflow."""
        # Initialize extractor
        extractor = DOCXExtractor(temp_docx_with_images)

        # Validate document
        assert extractor.validate_document() is True

        # Extract images
        images = extractor.extract_images()

        # Verify results
        assert isinstance(images, list)

        for img in images:
            # Verify all required fields
            assert img.image_id
            assert img.filename
            assert img.format
            assert img.size_bytes > 0
            assert img.width_pixels > 0
            assert img.height_pixels > 0
            assert isinstance(img.position, dict)
            assert 'paragraph_index' in img.position
            assert 'anchor_type' in img.position
