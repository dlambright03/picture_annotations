"""
Tests for JSON handler utilities.

Tests JSON and HTML report generation for alt-text results.
"""

import json
from pathlib import Path

import pytest

from ada_annotator.models import AltTextResult, ImageMetadata
from ada_annotator.utils.json_handler import (
    generate_html_output_path,
    generate_json_output_path,
    load_alt_text_from_json,
    save_alt_text_to_html,
    save_alt_text_to_json,
)


@pytest.fixture
def sample_images():
    """Create sample image metadata for testing."""
    return [
        ImageMetadata(
            image_id="img-1",
            filename="image1.png",
            format="PNG",
            size_bytes=1024,
            width_pixels=800,
            height_pixels=600,
            page_number=1,
            position={"x": 0, "y": 0},
            existing_alt_text=None,
            image_data=b"fake_image_data_1",
        ),
        ImageMetadata(
            image_id="img-2",
            filename="image2.jpg",
            format="JPEG",
            size_bytes=2048,
            width_pixels=1024,
            height_pixels=768,
            page_number=2,
            position={"x": 100, "y": 100},
            existing_alt_text="Old alt text",
            image_data=b"fake_image_data_2",
        ),
    ]


@pytest.fixture
def sample_results():
    """Create sample alt-text results for testing."""
    return [
        AltTextResult(
            image_id="img-1",
            alt_text="A beautiful landscape with mountains",
            is_decorative=False,
            confidence_score=0.95,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=150,
            processing_time_seconds=2.5,
        ),
        AltTextResult(
            image_id="img-2",
            alt_text="",
            is_decorative=True,
            confidence_score=0.8,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=50,
            processing_time_seconds=1.2,
        ),
    ]


class TestGenerateOutputPaths:
    """Test output path generation functions."""

    def test_generate_json_output_path(self):
        """Should generate correct JSON output path."""
        input_path = Path("document.docx")
        output_path = generate_json_output_path(input_path)

        assert output_path == Path("document_alttext.json")
        assert output_path.suffix == ".json"

    def test_generate_html_output_path(self):
        """Should generate correct HTML output path."""
        input_path = Path("document.docx")
        output_path = generate_html_output_path(input_path)

        assert output_path == Path("document_alttext.html")
        assert output_path.suffix == ".html"

    def test_generate_paths_with_different_extensions(self):
        """Should work with different file extensions."""
        for ext in [".docx", ".pptx", ".pdf"]:
            input_path = Path(f"document{ext}")

            json_path = generate_json_output_path(input_path)
            assert json_path == Path("document_alttext.json")

            html_path = generate_html_output_path(input_path)
            assert html_path == Path("document_alttext.html")


class TestSaveAltTextToJson:
    """Test JSON file generation."""

    def test_save_alt_text_to_json_creates_file(
        self, tmp_path, sample_results, sample_images
    ):
        """Should create JSON file with correct structure."""
        output_path = tmp_path / "output.json"
        source_doc = Path("test_document.docx")

        save_alt_text_to_json(
            sample_results, sample_images, output_path, source_doc
        )

        assert output_path.exists()

    def test_save_alt_text_to_json_content(
        self, tmp_path, sample_results, sample_images
    ):
        """Should save correct JSON content."""
        output_path = tmp_path / "output.json"
        source_doc = Path("test_document.docx")

        save_alt_text_to_json(
            sample_results, sample_images, output_path, source_doc
        )

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check structure
        assert data["version"] == "1.0"
        assert data["source_document"] == str(source_doc)
        assert data["document_type"] == "DOCX"
        assert data["total_images"] == 2
        assert data["processed_images"] == 2

        # Check alt-text results
        assert len(data["alt_text_results"]) == 2
        result = data["alt_text_results"][0]
        assert result["image_id"] == "img-1"
        assert result["alt_text"] == "A beautiful landscape with mountains"
        assert result["confidence_score"] == 0.95

        # Check images
        assert len(data["images"]) == 2
        img = data["images"][0]
        assert img["image_id"] == "img-1"
        assert img["format"] == "PNG"
        assert img["width_pixels"] == 800
        assert "image_data_base64" in img

    def test_save_alt_text_to_json_empty_lists(self, tmp_path):
        """Should handle empty lists gracefully."""
        output_path = tmp_path / "output.json"
        source_doc = Path("test.docx")

        save_alt_text_to_json([], [], output_path, source_doc)

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["total_images"] == 0
        assert data["processed_images"] == 0
        assert data["alt_text_results"] == []
        assert data["images"] == []


class TestSaveAltTextToHtml:
    """Test HTML report generation."""

    def test_save_alt_text_to_html_creates_file(
        self, tmp_path, sample_results, sample_images
    ):
        """Should create HTML file."""
        output_path = tmp_path / "output.html"
        source_doc = Path("test_document.docx")

        save_alt_text_to_html(
            sample_results, sample_images, output_path, source_doc
        )

        assert output_path.exists()

    def test_save_alt_text_to_html_content(
        self, tmp_path, sample_results, sample_images
    ):
        """Should generate valid HTML with correct content."""
        output_path = tmp_path / "output.html"
        source_doc = Path("test_document.docx")

        save_alt_text_to_html(
            sample_results, sample_images, output_path, source_doc
        )

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Check HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "</html>" in html_content

        # Check title includes document name
        assert "test_document.docx" in html_content

        # Check statistics are present
        assert "2" in html_content  # Total images
        assert "Total Images" in html_content

        # Check image IDs are present
        assert "img-1" in html_content
        assert "img-2" in html_content

        # Check alt-text is present
        assert "A beautiful landscape with mountains" in html_content

        # Check decorative badge
        assert "Decorative" in html_content

        # Check metadata
        assert "800 × 600 px" in html_content
        assert "1024 × 768 px" in html_content

    def test_save_alt_text_to_html_with_warnings(self, tmp_path, sample_images):
        """Should display validation warnings correctly."""
        results = [
            AltTextResult(
                image_id="img-1",
                alt_text="Test alt text",
                is_decorative=False,
                confidence_score=0.7,
                validation_passed=False,
                validation_warnings=["Alt text too short", "Missing context"],
                tokens_used=100,
                processing_time_seconds=1.5,
            ),
        ]

        output_path = tmp_path / "output.html"
        source_doc = Path("test.docx")

        save_alt_text_to_html(results, sample_images[:1], output_path, source_doc)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Check warnings are displayed
        assert "Alt text too short" in html_content
        assert "Missing context" in html_content
        assert "Validation Warnings" in html_content

    def test_save_alt_text_to_html_empty_lists(self, tmp_path):
        """Should handle empty lists gracefully."""
        output_path = tmp_path / "output.html"
        source_doc = Path("test.docx")

        save_alt_text_to_html([], [], output_path, source_doc)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert "<!DOCTYPE html>" in html_content
        assert "0" in html_content  # Should show 0 images


class TestLoadAltTextFromJson:
    """Test JSON loading functionality."""

    def test_load_alt_text_from_json(
        self, tmp_path, sample_results, sample_images
    ):
        """Should load JSON file correctly."""
        json_path = tmp_path / "test.json"
        source_doc = Path("test.docx")

        # First save
        save_alt_text_to_json(sample_results, sample_images, json_path, source_doc)

        # Then load
        data = load_alt_text_from_json(json_path)

        assert data["version"] == "1.0"
        assert data["total_images"] == 2
        assert len(data["alt_text_results"]) == 2
        assert len(data["images"]) == 2

    def test_load_alt_text_from_json_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing file."""
        json_path = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_alt_text_from_json(json_path)

    def test_load_alt_text_from_json_invalid_version(self, tmp_path):
        """Should raise ValueError for unsupported version."""
        json_path = tmp_path / "test.json"

        # Create JSON with wrong version
        data = {"version": "2.0"}
        with open(json_path, "w") as f:
            json.dump(data, f)

        with pytest.raises(ValueError, match="Unsupported JSON version"):
            load_alt_text_from_json(json_path)

    def test_load_alt_text_from_json_invalid_json(self, tmp_path):
        """Should raise error for invalid JSON."""
        json_path = tmp_path / "test.json"

        # Create invalid JSON
        with open(json_path, "w") as f:
            f.write("not valid json {")

        with pytest.raises(json.JSONDecodeError):
            load_alt_text_from_json(json_path)
