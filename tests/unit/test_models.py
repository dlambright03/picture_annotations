"""
Unit tests for Pydantic data models.
"""

import pytest
from datetime import datetime
from pathlib import Path

from ada_annotator.models import (
    AltTextResult,
    ContextData,
    DocumentProcessingResult,
    ImageMetadata,
)


class TestImageMetadata:
    """Tests for ImageMetadata model."""
    
    def test_valid_image_metadata(self):
        """Test creating valid ImageMetadata."""
        metadata = ImageMetadata(
            image_id="img-001",
            filename="test.jpg",
            format="JPEG",
            size_bytes=1024,
            width_pixels=800,
            height_pixels=600,
        )
        
        assert metadata.image_id == "img-001"
        assert metadata.filename == "test.jpg"
        assert metadata.format == "JPEG"
        assert metadata.size_bytes == 1024
        assert metadata.width_pixels == 800
        assert metadata.height_pixels == 600
        assert metadata.page_number is None
        assert metadata.existing_alt_text is None
    
    def test_invalid_format(self):
        """Test that invalid format raises validation error."""
        with pytest.raises(ValueError):
            ImageMetadata(
                image_id="img-001",
                filename="test.jpg",
                format="TIFF",  # Invalid
                size_bytes=1024,
                width_pixels=800,
                height_pixels=600,
            )
    
    def test_negative_size(self):
        """Test that negative size raises validation error."""
        with pytest.raises(ValueError):
            ImageMetadata(
                image_id="img-001",
                filename="test.jpg",
                format="JPEG",
                size_bytes=-100,  # Invalid
                width_pixels=800,
                height_pixels=600,
            )


class TestContextData:
    """Tests for ContextData model."""
    
    def test_valid_context_data(self):
        """Test creating valid ContextData."""
        context = ContextData(
            document_context="Test Document",
            local_context="This is a test image.",
        )
        
        assert context.document_context == "Test Document"
        assert context.local_context == "This is a test image."
        assert context.external_context is None
        assert context.section_context is None
        assert context.page_context is None
    
    def test_get_merged_context(self):
        """Test merging all context levels."""
        context = ContextData(
            external_context="External info",
            document_context="Doc title",
            section_context="Section heading",
            page_context="Page 1",
            local_context="Local text",
        )
        
        merged = context.get_merged_context()
        
        assert "[External Context] External info" in merged
        assert "[Document: Doc title]" in merged
        assert "[Section: Section heading]" in merged
        assert "[Page: Page 1]" in merged
        assert "[Local: Local text]" in merged
    
    def test_get_merged_context_truncation(self):
        """Test that long context gets truncated."""
        long_text = "x" * 15000
        context = ContextData(
            document_context="Test",
            local_context=long_text,
        )
        
        merged = context.get_merged_context(max_chars=1000)
        
        assert len(merged) <= 1003  # 1000 + "..."
        assert merged.endswith("...")


class TestAltTextResult:
    """Tests for AltTextResult model."""
    
    def test_valid_alt_text_result(self):
        """Test creating valid AltTextResult."""
        result = AltTextResult(
            image_id="img-001",
            alt_text="A test image",
            confidence_score=0.95,
            validation_passed=True,
            tokens_used=100,
            processing_time_seconds=1.5,
        )
        
        assert result.image_id == "img-001"
        assert result.alt_text == "A test image"
        assert result.confidence_score == 0.95
        assert result.validation_passed is True
        assert result.tokens_used == 100
        assert result.processing_time_seconds == 1.5
        assert isinstance(result.timestamp, datetime)
    
    def test_alt_text_too_long(self):
        """Test that alt-text > 250 chars raises error."""
        with pytest.raises(ValueError):
            AltTextResult(
                image_id="img-001",
                alt_text="x" * 251,  # Too long
                confidence_score=0.95,
                validation_passed=True,
                tokens_used=100,
                processing_time_seconds=1.5,
            )
    
    def test_invalid_confidence_score(self):
        """Test that confidence score outside 0-1 raises error."""
        with pytest.raises(ValueError):
            AltTextResult(
                image_id="img-001",
                alt_text="Test",
                confidence_score=1.5,  # > 1.0
                validation_passed=True,
                tokens_used=100,
                processing_time_seconds=1.5,
            )


class TestDocumentProcessingResult:
    """Tests for DocumentProcessingResult model."""
    
    def test_valid_processing_result(self):
        """Test creating valid DocumentProcessingResult."""
        result = DocumentProcessingResult(
            input_file=Path("test.docx"),
            output_file=Path("test_out.docx"),
            document_type="DOCX",
            total_images=10,
            successful_images=9,
            failed_images=1,
        )
        
        assert result.input_file == Path("test.docx")
        assert result.output_file == Path("test_out.docx")
        assert result.document_type == "DOCX"
        assert result.total_images == 10
        assert result.successful_images == 9
        assert result.failed_images == 1
        assert result.total_tokens_used == 0
        assert result.estimated_cost_usd == 0.0
        assert isinstance(result.timestamp, datetime)
    
    def test_negative_images(self):
        """Test that negative image counts raise error."""
        with pytest.raises(ValueError):
            DocumentProcessingResult(
                input_file=Path("test.docx"),
                output_file=Path("test_out.docx"),
                document_type="DOCX",
                total_images=-1,  # Invalid
            )
