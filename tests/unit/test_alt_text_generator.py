"""
Unit tests for AltTextGenerator orchestrator.

Tests the complete alt-text generation workflow including context
integration, AI service calls, validation, and result construction.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from ada_annotator.config import Settings
from ada_annotator.exceptions import APIError, ValidationError
from ada_annotator.generators.alt_text_generator import AltTextGenerator
from ada_annotator.models import (
    AltTextResult,
    ContextData,
    ImageMetadata,
)


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_api_key="test_key",
        azure_openai_deployment_name="gpt-4o",
        ai_temperature=0.3,
        ai_max_tokens=500,
    )


@pytest.fixture
def mock_ai_service():
    """Create mock AI service."""
    service = AsyncMock()
    service.generate_alt_text = AsyncMock(
        return_value="Diagram of plant cell showing nucleus and chloroplasts."
    )
    return service


@pytest.fixture
def mock_context_extractor():
    """Create mock context extractor."""
    extractor = Mock()
    extractor.extract_context_for_image = Mock(
        return_value=ContextData(
            external_context="Biology textbook",
            document_context="Chapter 5: Cell Structure",
            section_context="Plant Cells",
            page_context="Slide 10",
            local_context="This diagram shows the organelles.",
        )
    )
    return extractor


@pytest.fixture
def sample_image_metadata():
    """Create sample image metadata."""
    return ImageMetadata(
        image_id="img_001",
        filename="test_image.png",
        format="PNG",
        size_bytes=50000,
        width_pixels=800,
        height_pixels=600,
        page_number=5,
        position={"paragraph_index": 10, "anchor_type": "inline"},
    )


@pytest.fixture
def generator(settings, mock_ai_service, mock_context_extractor):
    """Create AltTextGenerator instance."""
    return AltTextGenerator(
        settings=settings,
        ai_service=mock_ai_service,
        context_extractor=mock_context_extractor,
    )


# ============================================================================
# Initialization Tests
# ============================================================================


def test_initialization_with_valid_dependencies(
    settings, mock_ai_service, mock_context_extractor
):
    """Test initialization with valid dependencies."""
    generator = AltTextGenerator(
        settings=settings,
        ai_service=mock_ai_service,
        context_extractor=mock_context_extractor,
    )

    assert generator.settings == settings
    assert generator.ai_service == mock_ai_service
    assert generator.context_extractor == mock_context_extractor


def test_initialization_stores_settings(generator, settings):
    """Test that settings are stored correctly."""
    assert generator.settings.ai_temperature == 0.3
    assert generator.settings.ai_max_tokens == 500


def test_initialization_injects_dependencies(
    generator, mock_ai_service, mock_context_extractor
):
    """Test dependency injection works."""
    assert generator.ai_service is mock_ai_service
    assert generator.context_extractor is mock_context_extractor


# ============================================================================
# Single Image Generation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_generate_for_image_happy_path(
    generator, sample_image_metadata
):
    """Test successful alt-text generation for single image."""
    result = await generator.generate_for_image(sample_image_metadata)

    assert isinstance(result, AltTextResult)
    assert result.image_id == "img_001"
    assert result.alt_text == (
        "Diagram of plant cell showing nucleus and chloroplasts."
    )
    assert result.validation_passed is True
    assert result.tokens_used > 0
    assert result.processing_time_seconds >= 0


@pytest.mark.asyncio
async def test_generate_uses_context_extractor(
    generator, sample_image_metadata, mock_context_extractor
):
    """Test that context extractor is called."""
    await generator.generate_for_image(sample_image_metadata)

    mock_context_extractor.extract_context_for_image.assert_called_once_with(
        sample_image_metadata
    )


@pytest.mark.asyncio
async def test_generate_passes_context_to_ai(
    generator, sample_image_metadata, mock_ai_service
):
    """Test that merged context is passed to AI service."""
    await generator.generate_for_image(sample_image_metadata)

    mock_ai_service.generate_alt_text.assert_called_once()
    call_args = mock_ai_service.generate_alt_text.call_args
    assert sample_image_metadata in call_args[0]
    # Context should be string from get_merged_context()
    assert isinstance(call_args[0][1], str)


@pytest.mark.asyncio
async def test_generate_tracks_processing_time(
    generator, sample_image_metadata
):
    """Test that processing time is tracked."""
    result = await generator.generate_for_image(sample_image_metadata)

    assert result.processing_time_seconds >= 0
    assert isinstance(result.processing_time_seconds, float)


@pytest.mark.asyncio
async def test_generate_validates_alt_text(
    generator, sample_image_metadata
):
    """Test that alt-text goes through validation."""
    result = await generator.generate_for_image(sample_image_metadata)

    assert result.validation_passed is True
    assert isinstance(result.validation_warnings, list)


@pytest.mark.asyncio
async def test_generate_with_validation_warnings(
    generator, sample_image_metadata, mock_ai_service
):
    """Test generation with alt-text that triggers warnings."""
    # Short alt-text (< 50 chars) should trigger warning
    mock_ai_service.generate_alt_text.return_value = "Plant cell diagram"

    result = await generator.generate_for_image(sample_image_metadata)

    assert result.validation_passed is True
    assert len(result.validation_warnings) > 0
    assert any("short" in w.lower() for w in result.validation_warnings)


@pytest.mark.asyncio
async def test_generate_with_context_extraction_error(
    generator, sample_image_metadata, mock_context_extractor
):
    """Test graceful handling of context extraction errors."""
    mock_context_extractor.extract_context_for_image.side_effect = (
        Exception("Context error")
    )

    # Should use minimal context and continue
    result = await generator.generate_for_image(sample_image_metadata)

    assert isinstance(result, AltTextResult)
    assert result.image_id == "img_001"


@pytest.mark.asyncio
async def test_generate_with_ai_service_error(
    generator, sample_image_metadata, mock_ai_service
):
    """Test handling of AI service errors."""
    mock_ai_service.generate_alt_text.side_effect = APIError(
        "API timeout", status_code=504
    )

    with pytest.raises(APIError) as exc_info:
        await generator.generate_for_image(sample_image_metadata)

    assert exc_info.value.status_code == 504


# ============================================================================
# Batch Generation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_generate_for_multiple_images_all_succeed(
    generator, sample_image_metadata
):
    """Test batch processing with all images successful."""
    images = [
        sample_image_metadata,
        ImageMetadata(
            image_id="img_002",
            filename="test2.png",
            format="PNG",
            size_bytes=60000,
            width_pixels=1024,
            height_pixels=768,
            page_number=6,
            position={"paragraph_index": 15, "anchor_type": "floating"},
        ),
    ]

    results = await generator.generate_for_multiple_images(images)

    assert len(results) == 2
    assert all(isinstance(r, AltTextResult) for r in results)
    assert results[0].image_id == "img_001"
    assert results[1].image_id == "img_002"


@pytest.mark.asyncio
async def test_generate_for_multiple_with_partial_failure(
    generator, sample_image_metadata, mock_ai_service
):
    """Test batch processing with some failures."""
    images = [
        sample_image_metadata,
        ImageMetadata(
            image_id="img_002",
            filename="test2.png",
            format="PNG",
            size_bytes=60000,
            width_pixels=1024,
            height_pixels=768,
            page_number=6,
            position={"paragraph_index": 15, "anchor_type": "floating"},
        ),
    ]

    # First call succeeds, second fails
    mock_ai_service.generate_alt_text.side_effect = [
        "First alt-text description.",
        APIError("Rate limited", status_code=429),
    ]

    results = await generator.generate_for_multiple_images(
        images, continue_on_error=True
    )

    # Should get one successful result
    assert len(results) == 1
    assert results[0].image_id == "img_001"


@pytest.mark.asyncio
async def test_generate_for_multiple_tracks_progress(
    generator, sample_image_metadata
):
    """Test that progress callback is invoked during batch."""
    images = [sample_image_metadata] * 3
    progress_calls = []

    def progress_callback(current, total):
        progress_calls.append((current, total))

    await generator.generate_for_multiple_images(
        images, progress_callback=progress_callback
    )

    assert len(progress_calls) == 3
    assert progress_calls[-1] == (3, 3)


@pytest.mark.asyncio
async def test_generate_for_empty_list(generator):
    """Test batch processing with empty image list."""
    results = await generator.generate_for_multiple_images([])

    assert results == []


# ============================================================================
# Validation Tests
# ============================================================================


def test_validate_alt_text_passes_valid_text(generator):
    """Test validation with valid alt-text."""
    alt_text = (
        "Diagram showing the structure of a plant cell "
        "with labeled organelles."
    )

    passed, warnings = generator._validate_alt_text(alt_text)

    assert passed is True
    assert len(warnings) == 0


def test_validate_alt_text_length_minimum(generator):
    """Test validation rejects text below minimum length."""
    alt_text = "Cell"  # Only 4 chars

    passed, warnings = generator._validate_alt_text(alt_text)

    assert passed is False
    assert any("minimum" in w.lower() for w in warnings)


def test_validate_alt_text_length_maximum(generator):
    """Test validation rejects text above maximum length."""
    alt_text = "A" * 300  # 300 chars, exceeds 250 limit

    passed, warnings = generator._validate_alt_text(alt_text)

    assert passed is False
    assert any("maximum" in w.lower() for w in warnings)


def test_validate_alt_text_warns_short(generator):
    """Test validation warns for short but acceptable text."""
    alt_text = "Plant cell diagram."  # Valid but < 50 chars

    passed, warnings = generator._validate_alt_text(alt_text)

    assert passed is True
    assert len(warnings) > 0
    assert any("short" in w.lower() for w in warnings)


def test_validate_alt_text_warns_long(generator):
    """Test validation warns for long but acceptable text."""
    alt_text = "A" * 220  # Valid but > 200 chars

    passed, warnings = generator._validate_alt_text(alt_text)

    assert passed is True
    assert len(warnings) > 0
    assert any("long" in w.lower() for w in warnings)


def test_validate_alt_text_forbidden_phrases(generator):
    """Test validation detects forbidden phrases."""
    forbidden_texts = [
        "Image of a plant cell",
        "Picture of the diagram",
        "Graphic showing cell structure",
    ]

    for text in forbidden_texts:
        passed, warnings = generator._validate_alt_text(text)
        assert passed is False
        assert any("forbidden" in w.lower() for w in warnings)


def test_validate_alt_text_capitalization(generator):
    """Test validation checks first character is uppercase."""
    alt_text = "diagram of plant cell with labeled parts."

    passed, warnings = generator._validate_alt_text(alt_text)

    # Should warn about capitalization
    assert any(
        "capital" in w.lower() or "uppercase" in w.lower()
        for w in warnings
    )


def test_validate_alt_text_auto_adds_period(generator):
    """Test that missing period is auto-corrected."""
    alt_text = "Diagram of plant cell showing nucleus"

    corrected = generator._auto_correct_alt_text(alt_text)

    assert corrected.endswith(".")


def test_validate_alt_text_whitespace_trimming(generator):
    """Test that excessive whitespace is removed."""
    alt_text = "  Diagram  of   plant cell.  "

    corrected = generator._auto_correct_alt_text(alt_text)

    assert corrected == "Diagram of plant cell."
    assert "  " not in corrected


# ============================================================================
# Cost Calculation Tests
# ============================================================================


def test_calculate_cost_with_tokens(generator):
    """Test cost calculation from token usage."""
    # Using approximate Azure OpenAI GPT-4o pricing
    input_tokens = 1500
    output_tokens = 50

    cost = generator._calculate_cost(input_tokens, output_tokens)

    assert cost > 0
    assert isinstance(cost, float)
    # Rough estimate: should be a few cents
    assert 0.001 < cost < 0.1


def test_calculate_cost_zero_tokens(generator):
    """Test cost calculation with zero tokens."""
    cost = generator._calculate_cost(0, 0)

    assert cost == 0.0


def test_calculate_cost_large_token_count(generator):
    """Test cost calculation with large token count."""
    input_tokens = 10000
    output_tokens = 500

    cost = generator._calculate_cost(input_tokens, output_tokens)

    assert cost > 0
    assert isinstance(cost, float)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_complete_workflow_with_real_components(
    settings, sample_image_metadata, tmp_path
):
    """Test complete workflow with minimal mocking."""
    # Mock only the AI service call
    mock_ai = AsyncMock()
    mock_ai.generate_alt_text = AsyncMock(
        return_value="Complete diagram of plant cell structure."
    )

    # Create a temporary DOCX file for testing
    from docx import Document
    doc = Document()
    doc.core_properties.title = "Biology Textbook"
    doc_path = tmp_path / "test.docx"
    doc.save(str(doc_path))

    # Use real context extractor
    from ada_annotator.utils.context_extractor import ContextExtractor

    context_extractor = ContextExtractor(
        document_path=doc_path,
    )

    generator = AltTextGenerator(
        settings=settings,
        ai_service=mock_ai,
        context_extractor=context_extractor,
    )

    result = await generator.generate_for_image(sample_image_metadata)

    assert isinstance(result, AltTextResult)
    assert result.validation_passed is True
    assert result.alt_text == "Complete diagram of plant cell structure."
