"""
Unit tests for PPTX image extractor.

Tests PPTX image extraction with position metadata, slide context,
and existing alt-text extraction.
"""

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Inches

from ada_annotator.document_processors import PPTXExtractor
from ada_annotator.exceptions import ProcessingError


class TestPPTXExtractorInitialization:
    """Test PPTXExtractor initialization and validation."""

    def test_initialization_success(self, tmp_path):
        """Test successful initialization with valid PPTX."""
        # Create minimal PPTX
        pptx_path = tmp_path / "test.pptx"
        prs = Presentation()
        prs.save(str(pptx_path))

        extractor = PPTXExtractor(pptx_path)

        assert extractor.document_path == pptx_path
        assert extractor.get_document_format() == "PPTX"
        assert extractor.presentation is not None

    def test_initialization_file_not_found(self, tmp_path):
        """Test initialization with non-existent file."""
        pptx_path = tmp_path / "nonexistent.pptx"

        with pytest.raises(FileNotFoundError):
            PPTXExtractor(pptx_path)

    def test_initialization_wrong_extension(self, tmp_path):
        """Test initialization with wrong file extension."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("Not a PPTX file")

        with pytest.raises(ValueError, match="Not a PPTX file"):
            PPTXExtractor(txt_path)

    def test_initialization_corrupted_file(self, tmp_path):
        """Test initialization with corrupted PPTX."""
        pptx_path = tmp_path / "corrupted.pptx"
        pptx_path.write_bytes(b"Not a valid PPTX file")

        with pytest.raises(ProcessingError):
            PPTXExtractor(pptx_path)

    def test_validate_document(self, tmp_path):
        """Test document validation."""
        pptx_path = tmp_path / "test.pptx"
        prs = Presentation()
        prs.save(str(pptx_path))

        extractor = PPTXExtractor(pptx_path)
        assert extractor.validate_document() is True


class TestPPTXImageExtraction:
    """Test PPTX image extraction functionality."""

    def test_extract_images_empty_presentation(self, tmp_path):
        """Test extraction from presentation with no images."""
        pptx_path = tmp_path / "empty.pptx"
        prs = Presentation()
        prs.slides.add_slide(prs.slide_layouts[0])  # Blank slide
        prs.save(str(pptx_path))

        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 0

    def test_extract_single_image(self, tmp_path):
        """Test extraction of single image from slide."""
        # Create test image
        img_bytes = BytesIO()
        test_img = Image.new("RGB", (100, 100), color="red")
        test_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Create PPTX with image
        pptx_path = tmp_path / "single_image.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
        slide.shapes.add_picture(
            img_bytes,
            Inches(1),
            Inches(1),
            Inches(2),
            Inches(2)
        )
        prs.save(str(pptx_path))

        # Extract and verify
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 1
        assert images[0].format == "PNG"
        assert images[0].width_pixels == 100
        assert images[0].height_pixels == 100
        assert images[0].page_number == 1

    def test_extract_multiple_images_single_slide(self, tmp_path):
        """Test extraction of multiple images from one slide."""
        # Create test images
        img1_bytes = BytesIO()
        test_img1 = Image.new("RGB", (50, 50), color="red")
        test_img1.save(img1_bytes, format="PNG")
        img1_bytes.seek(0)

        img2_bytes = BytesIO()
        test_img2 = Image.new("RGB", (60, 60), color="blue")
        test_img2.save(img2_bytes, format="PNG")
        img2_bytes.seek(0)

        # Create PPTX
        pptx_path = tmp_path / "multi_image.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.shapes.add_picture(
            img1_bytes, Inches(1), Inches(1), Inches(1), Inches(1)
        )
        slide.shapes.add_picture(
            img2_bytes, Inches(3), Inches(3), Inches(1), Inches(1)
        )
        prs.save(str(pptx_path))

        # Extract and verify
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 2
        assert images[0].width_pixels == 50
        assert images[1].width_pixels == 60

    def test_extract_images_multiple_slides(self, tmp_path):
        """Test extraction from multiple slides."""
        # Create test image
        img_bytes = BytesIO()
        test_img = Image.new("RGB", (40, 40), color="green")
        test_img.save(img_bytes, format="PNG")

        # Create PPTX with multiple slides
        pptx_path = tmp_path / "multi_slide.pptx"
        prs = Presentation()

        for i in range(3):
            img_bytes.seek(0)
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.shapes.add_picture(
                img_bytes,
                Inches(1),
                Inches(1),
                Inches(1),
                Inches(1)
            )

        prs.save(str(pptx_path))

        # Extract and verify
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 3
        assert images[0].page_number == 1
        assert images[1].page_number == 2
        assert images[2].page_number == 3


class TestPPTXPositionMetadata:
    """Test position metadata extraction."""

    def test_position_metadata_captured(self, tmp_path):
        """Test that position metadata is captured correctly."""
        # Create test image
        img_bytes = BytesIO()
        test_img = Image.new("RGB", (100, 100), color="blue")
        test_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Create PPTX
        pptx_path = tmp_path / "position.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        pic = slide.shapes.add_picture(
            img_bytes,
            Inches(2),
            Inches(3),
            Inches(4),
            Inches(5)
        )
        prs.save(str(pptx_path))

        # Extract and verify position
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 1
        position = images[0].position
        assert "slide_index" in position
        assert "shape_index" in position
        assert "left_emu" in position
        assert "top_emu" in position
        assert "width_emu" in position
        assert "height_emu" in position
        assert position["slide_index"] == 0
        assert position["shape_index"] >= 0

    def test_slide_title_extracted(self, tmp_path):
        """Test that slide titles are captured as context."""
        # Create test image
        img_bytes = BytesIO()
        test_img = Image.new("RGB", (50, 50), color="yellow")
        test_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Create PPTX with title
        pptx_path = tmp_path / "titled.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])  # Title
        slide.shapes.title.text = "Test Slide Title"
        slide.shapes.add_picture(
            img_bytes, Inches(1), Inches(2), Inches(1), Inches(1)
        )
        prs.save(str(pptx_path))

        # Extract and verify
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 1
        position = images[0].position
        assert position.get("slide_title") == "Test Slide Title"

    def test_slide_no_title(self, tmp_path):
        """Test handling of slides without titles."""
        # Create test image
        img_bytes = BytesIO()
        test_img = Image.new("RGB", (50, 50), color="purple")
        test_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Create PPTX without title
        pptx_path = tmp_path / "notitle.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
        slide.shapes.add_picture(
            img_bytes, Inches(1), Inches(1), Inches(1), Inches(1)
        )
        prs.save(str(pptx_path))

        # Extract and verify
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 1
        position = images[0].position
        assert position.get("slide_title") is None


class TestPPTXAltTextExtraction:
    """Test existing alt-text extraction from PPTX."""

    def test_image_id_generation(self, tmp_path):
        """Test unique image ID generation."""
        # Create test images
        img_bytes = BytesIO()
        test_img = Image.new("RGB", (30, 30), color="cyan")
        test_img.save(img_bytes, format="PNG")

        # Create PPTX
        pptx_path = tmp_path / "ids.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        img_bytes.seek(0)
        slide.shapes.add_picture(
            img_bytes, Inches(1), Inches(1), Inches(1), Inches(1)
        )

        img_bytes.seek(0)
        slide.shapes.add_picture(
            img_bytes, Inches(3), Inches(3), Inches(1), Inches(1)
        )

        prs.save(str(pptx_path))

        # Extract and verify IDs are unique
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 2
        assert images[0].image_id != images[1].image_id
        assert "slide0" in images[0].image_id
        assert "shape" in images[0].image_id


class TestPPTXEdgeCases:
    """Test edge cases and error handling."""

    def test_non_picture_shapes_ignored(self, tmp_path):
        """Test that non-picture shapes are ignored."""
        pptx_path = tmp_path / "shapes.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # Add text box (not a picture)
        txBox = slide.shapes.add_textbox(
            Inches(1), Inches(1), Inches(2), Inches(1)
        )
        txBox.text = "Test text"

        prs.save(str(pptx_path))

        # Extract - should find no images
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 0

    def test_format_normalization(self, tmp_path):
        """Test that image formats are normalized."""
        # Create JPEG image
        img_bytes = BytesIO()
        test_img = Image.new("RGB", (50, 50), color="orange")
        test_img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        pptx_path = tmp_path / "jpeg.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.shapes.add_picture(
            img_bytes, Inches(1), Inches(1), Inches(1), Inches(1)
        )
        prs.save(str(pptx_path))

        # Extract and verify format
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        assert len(images) == 1
        assert images[0].format == "JPEG"


class TestPPTXIntegration:
    """Integration tests for complete PPTX processing."""

    def test_complete_extraction_workflow(self, tmp_path):
        """Test complete extraction with multiple slides and images."""
        # Create multiple test images
        red_img = BytesIO()
        Image.new("RGB", (100, 100), "red").save(red_img, "PNG")

        blue_img = BytesIO()
        Image.new("RGB", (200, 200), "blue").save(blue_img, "PNG")

        # Create complex PPTX
        pptx_path = tmp_path / "complex.pptx"
        prs = Presentation()

        # Slide 1: Title slide with image
        slide1 = prs.slides.add_slide(prs.slide_layouts[0])
        slide1.shapes.title.text = "Slide 1 Title"
        red_img.seek(0)
        slide1.shapes.add_picture(
            red_img, Inches(1), Inches(2), Inches(2), Inches(2)
        )

        # Slide 2: Blank slide with two images
        slide2 = prs.slides.add_slide(prs.slide_layouts[6])
        red_img.seek(0)
        slide2.shapes.add_picture(
            red_img, Inches(0.5), Inches(0.5), Inches(1), Inches(1)
        )
        blue_img.seek(0)
        slide2.shapes.add_picture(
            blue_img, Inches(4), Inches(4), Inches(3), Inches(3)
        )

        prs.save(str(pptx_path))

        # Extract and verify
        extractor = PPTXExtractor(pptx_path)
        images = extractor.extract_images()

        # Should have 3 total images
        assert len(images) == 3

        # Verify slide distribution
        slide_numbers = [img.page_number for img in images]
        assert slide_numbers.count(1) == 1  # 1 image on slide 1
        assert slide_numbers.count(2) == 2  # 2 images on slide 2

        # Verify dimensions
        assert images[0].width_pixels == 100
        assert images[2].width_pixels == 200

        # Verify position metadata exists
        for img in images:
            assert "slide_index" in img.position
            assert "left_emu" in img.position
            assert "width_emu" in img.position
