"""
Unit tests for image utility functions.

Tests image-to-base64 conversion and related image operations.
"""

import base64
from pathlib import Path

import pytest
from PIL import Image

from ada_annotator.utils.image_utils import (
    convert_image_to_base64,
    get_image_format,
    validate_image_file,
)


@pytest.fixture
def temp_image_file(tmp_path):
    """Create a temporary test image file."""
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path, "PNG")
    return img_path


@pytest.fixture
def temp_jpeg_file(tmp_path):
    """Create a temporary JPEG test image."""
    img_path = tmp_path / "test_image.jpg"
    img = Image.new("RGB", (50, 50), color="blue")
    img.save(img_path, "JPEG")
    return img_path


class TestConvertImageToBase64:
    """Test suite for convert_image_to_base64 function."""

    def test_converts_png_image_successfully(self, temp_image_file):
        """Should convert PNG image to base64 string."""
        result = convert_image_to_base64(temp_image_file)

        assert isinstance(result, str)
        assert len(result) > 0
        # Verify it's valid base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_converts_jpeg_image_successfully(self, temp_jpeg_file):
        """Should convert JPEG image to base64 string."""
        result = convert_image_to_base64(temp_jpeg_file)

        assert isinstance(result, str)
        assert len(result) > 0
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_includes_data_uri_prefix_when_requested(self, temp_image_file):
        """Should add data URI prefix if include_prefix=True."""
        result = convert_image_to_base64(temp_image_file, include_prefix=True)

        assert result.startswith("data:image/")
        assert ";base64," in result

    def test_without_data_uri_prefix_by_default(self, temp_image_file):
        """Should not include data URI prefix by default."""
        result = convert_image_to_base64(temp_image_file)

        assert not result.startswith("data:")
        # Should be pure base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_handles_path_object(self, temp_image_file):
        """Should accept pathlib.Path objects."""
        result = convert_image_to_base64(temp_image_file)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_handles_string_path(self, temp_image_file):
        """Should accept string paths."""
        result = convert_image_to_base64(str(temp_image_file))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_raises_error_for_nonexistent_file(self):
        """Should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            convert_image_to_base64("nonexistent_file.png")

    def test_raises_error_for_corrupted_image(self, tmp_path):
        """Should raise ValueError for corrupted image files."""
        bad_file = tmp_path / "corrupted.png"
        bad_file.write_text("This is not an image")

        with pytest.raises((ValueError, IOError)):
            convert_image_to_base64(bad_file)

    def test_handles_different_image_formats(self, tmp_path):
        """Should handle various image formats."""
        formats = ["PNG", "JPEG", "BMP"]

        for fmt in formats:
            img_path = tmp_path / f"test.{fmt.lower()}"
            img = Image.new("RGB", (10, 10), color="green")
            img.save(img_path, fmt)

            result = convert_image_to_base64(img_path)
            assert isinstance(result, str)
            assert len(result) > 0


class TestGetImageFormat:
    """Test suite for get_image_format function."""

    def test_detects_png_format(self, temp_image_file):
        """Should detect PNG format."""
        fmt = get_image_format(temp_image_file)
        assert fmt.upper() == "PNG"

    def test_detects_jpeg_format(self, temp_jpeg_file):
        """Should detect JPEG format."""
        fmt = get_image_format(temp_jpeg_file)
        assert fmt.upper() in ["JPEG", "JPG"]

    def test_handles_path_object(self, temp_image_file):
        """Should work with Path objects."""
        fmt = get_image_format(temp_image_file)
        assert fmt is not None

    def test_handles_string_path(self, temp_image_file):
        """Should work with string paths."""
        fmt = get_image_format(str(temp_image_file))
        assert fmt is not None

    def test_raises_error_for_nonexistent_file(self):
        """Should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_image_format("nonexistent.png")


class TestValidateImageFile:
    """Test suite for validate_image_file function."""

    def test_validates_valid_png_image(self, temp_image_file):
        """Should return True for valid PNG."""
        assert validate_image_file(temp_image_file) is True

    def test_validates_valid_jpeg_image(self, temp_jpeg_file):
        """Should return True for valid JPEG."""
        assert validate_image_file(temp_jpeg_file) is True

    def test_returns_false_for_nonexistent_file(self):
        """Should return False for missing files."""
        assert validate_image_file("nonexistent.png") is False

    def test_returns_false_for_corrupted_file(self, tmp_path):
        """Should return False for corrupted images."""
        bad_file = tmp_path / "bad.png"
        bad_file.write_text("Not an image")
        assert validate_image_file(bad_file) is False

    def test_returns_false_for_non_image_file(self, tmp_path):
        """Should return False for non-image files."""
        text_file = tmp_path / "document.txt"
        text_file.write_text("Hello world")
        assert validate_image_file(text_file) is False
