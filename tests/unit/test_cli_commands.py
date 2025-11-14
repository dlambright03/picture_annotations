"""Unit tests for CLI command handlers (command_extract, command_apply)."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import structlog

from ada_annotator.cli import command_extract, command_apply
from ada_annotator.exceptions import EXIT_SUCCESS, EXIT_INPUT_ERROR
from ada_annotator.models import ImageMetadata, AltTextResult


@pytest.fixture
def mock_logger():
    """Create mock structured logger."""
    # Use MagicMock without spec so it accepts any method call
    return MagicMock()


@pytest.fixture
def sample_images():
    """Create sample image metadata list."""
    return [
        ImageMetadata(
            image_id="img_001",
            filename="test.png",
            format="PNG",
            size_bytes=100,
            width_pixels=100,
            height_pixels=100,
            page_number=1,
            position={},
            existing_alt_text=None,
            image_data=None,
        ),
        ImageMetadata(
            image_id="img_002",
            filename="test2.png",
            format="PNG",
            size_bytes=200,
            width_pixels=200,
            height_pixels=200,
            page_number=1,
            position={},
            existing_alt_text=None,
            image_data=None,
        ),
    ]


@pytest.fixture
def sample_alt_text_results():
    """Create sample alt-text results."""
    return [
        AltTextResult(
            image_id="img_001",
            alt_text="A red diagram",
            is_decorative=False,
            confidence_score=0.95,
            validation_passed=True,
            tokens_used=50,
            processing_time_seconds=1.5,
        ),
        AltTextResult(
            image_id="img_002",
            alt_text="A blue chart",
            is_decorative=False,
            confidence_score=0.90,
            validation_passed=True,
            tokens_used=45,
            processing_time_seconds=1.3,
        ),
    ]


class TestCommandExtract:
    """Tests for command_extract function."""

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.save_alt_text_to_html')
    @patch('ada_annotator.cli.save_alt_text_to_json')
    @patch('ada_annotator.cli.generate_html_output_path')
    @patch('ada_annotator.cli.AltTextGenerator')
    @patch('ada_annotator.cli.ContextExtractor')
    @patch('ada_annotator.cli.SemanticKernelService')
    @patch('ada_annotator.cli.Settings')
    @patch('ada_annotator.cli.DOCXExtractor')
    async def test_extract_docx_success(
        self,
        mock_extractor_class,
        mock_settings_class,
        mock_service_class,
        mock_context_class,
        mock_generator_class,
        mock_html_path,
        mock_save_json,
        mock_save_html,
        tmp_path,
        mock_logger,
        sample_images,
        sample_alt_text_results,
    ):
        """Should successfully extract images and generate alt-text for DOCX."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")
        output_file = tmp_path / "output.json"

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_for_multiple_images = AsyncMock(
            return_value=sample_alt_text_results
        )
        mock_generator_class.return_value = mock_generator

        # Mock HTML path
        mock_html_path.return_value = tmp_path / "output.html"

        # Execute
        result = await command_extract(
            input_path=input_file,
            output_path=output_file,
            context_path=None,
            max_images=None,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        mock_extractor_class.assert_called_once_with(input_file)
        mock_extractor.extract_images.assert_called_once()
        mock_generator.generate_for_multiple_images.assert_called_once()
        mock_save_json.assert_called_once()
        mock_save_html.assert_called_once()

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.save_alt_text_to_html')
    @patch('ada_annotator.cli.save_alt_text_to_json')
    @patch('ada_annotator.cli.generate_html_output_path')
    @patch('ada_annotator.cli.AltTextGenerator')
    @patch('ada_annotator.cli.ContextExtractor')
    @patch('ada_annotator.cli.SemanticKernelService')
    @patch('ada_annotator.cli.Settings')
    @patch('ada_annotator.cli.PPTXExtractor')
    async def test_extract_pptx_success(
        self,
        mock_extractor_class,
        mock_settings_class,
        mock_service_class,
        mock_context_class,
        mock_generator_class,
        mock_html_path,
        mock_save_json,
        mock_save_html,
        tmp_path,
        mock_logger,
        sample_images,
        sample_alt_text_results,
    ):
        """Should successfully extract images from PPTX."""
        # Setup
        input_file = tmp_path / "test.pptx"
        input_file.write_text("test")
        output_file = tmp_path / "output.json"

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_for_multiple_images = AsyncMock(
            return_value=sample_alt_text_results
        )
        mock_generator_class.return_value = mock_generator

        # Mock HTML path
        mock_html_path.return_value = tmp_path / "output.html"

        # Execute
        result = await command_extract(
            input_path=input_file,
            output_path=output_file,
            context_path=None,
            max_images=None,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        mock_extractor_class.assert_called_once_with(input_file)

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.save_alt_text_to_html')
    @patch('ada_annotator.cli.save_alt_text_to_json')
    @patch('ada_annotator.cli.generate_html_output_path')
    @patch('ada_annotator.cli.AltTextGenerator')
    @patch('ada_annotator.cli.ContextExtractor')
    @patch('ada_annotator.cli.SemanticKernelService')
    @patch('ada_annotator.cli.Settings')
    @patch('ada_annotator.cli.PDFExtractor')
    async def test_extract_pdf_success(
        self,
        mock_extractor_class,
        mock_settings_class,
        mock_service_class,
        mock_context_class,
        mock_generator_class,
        mock_html_path,
        mock_save_json,
        mock_save_html,
        tmp_path,
        mock_logger,
        sample_images,
        sample_alt_text_results,
    ):
        """Should successfully extract images from PDF."""
        # Setup
        input_file = tmp_path / "test.pdf"
        input_file.write_text("test")
        output_file = tmp_path / "output.json"

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_for_multiple_images = AsyncMock(
            return_value=sample_alt_text_results
        )
        mock_generator_class.return_value = mock_generator

        # Mock HTML path
        mock_html_path.return_value = tmp_path / "output.html"

        # Execute
        result = await command_extract(
            input_path=input_file,
            output_path=output_file,
            context_path=None,
            max_images=None,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        mock_extractor_class.assert_called_once_with(input_file)

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.DOCXExtractor')
    async def test_extract_no_images_found(
        self,
        mock_extractor_class,
        tmp_path,
        mock_logger,
    ):
        """Should handle case when no images are found."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")
        output_file = tmp_path / "output.json"

        # Mock extractor returning empty list
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = []
        mock_extractor_class.return_value = mock_extractor

        # Execute
        result = await command_extract(
            input_path=input_file,
            output_path=output_file,
            context_path=None,
            max_images=None,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        mock_logger.warning.assert_called_once_with("no_images_found")

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.save_alt_text_to_html')
    @patch('ada_annotator.cli.save_alt_text_to_json')
    @patch('ada_annotator.cli.generate_html_output_path')
    @patch('ada_annotator.cli.AltTextGenerator')
    @patch('ada_annotator.cli.ContextExtractor')
    @patch('ada_annotator.cli.SemanticKernelService')
    @patch('ada_annotator.cli.Settings')
    @patch('ada_annotator.cli.DOCXExtractor')
    async def test_extract_with_max_images_limit(
        self,
        mock_extractor_class,
        mock_settings_class,
        mock_service_class,
        mock_context_class,
        mock_generator_class,
        mock_html_path,
        mock_save_json,
        mock_save_html,
        tmp_path,
        mock_logger,
        sample_images,
        sample_alt_text_results,
    ):
        """Should respect max_images limit."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")
        output_file = tmp_path / "output.json"

        # Create more images than limit
        many_images = sample_images * 5  # 10 images

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = many_images
        mock_extractor_class.return_value = mock_extractor

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_for_multiple_images = AsyncMock(
            return_value=sample_alt_text_results[:2]  # Only 2 results
        )
        mock_generator_class.return_value = mock_generator

        # Mock HTML path
        mock_html_path.return_value = tmp_path / "output.html"

        # Execute with max_images=2
        result = await command_extract(
            input_path=input_file,
            output_path=output_file,
            context_path=None,
            max_images=2,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        # Check that generator was called with limited images
        call_args = mock_generator.generate_for_multiple_images.call_args
        assert len(call_args[0][0]) == 2  # Only 2 images passed

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.save_alt_text_to_html')
    @patch('ada_annotator.cli.save_alt_text_to_json')
    @patch('ada_annotator.cli.generate_html_output_path')
    @patch('ada_annotator.cli.AltTextGenerator')
    @patch('ada_annotator.cli.ContextExtractor')
    @patch('ada_annotator.cli.SemanticKernelService')
    @patch('ada_annotator.cli.Settings')
    @patch('ada_annotator.cli.DOCXExtractor')
    async def test_extract_with_context_file(
        self,
        mock_extractor_class,
        mock_settings_class,
        mock_service_class,
        mock_context_class,
        mock_generator_class,
        mock_html_path,
        mock_save_json,
        mock_save_html,
        tmp_path,
        mock_logger,
        sample_images,
        sample_alt_text_results,
    ):
        """Should use context file when provided."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")
        output_file = tmp_path / "output.json"
        context_file = tmp_path / "context.txt"
        context_file.write_text("Document context")

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_for_multiple_images = AsyncMock(
            return_value=sample_alt_text_results
        )
        mock_generator_class.return_value = mock_generator

        # Mock HTML path
        mock_html_path.return_value = tmp_path / "output.html"

        # Execute
        result = await command_extract(
            input_path=input_file,
            output_path=output_file,
            context_path=context_file,
            max_images=None,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        # Verify ContextExtractor was initialized with context file
        mock_context_class.assert_called_once()
        call_kwargs = mock_context_class.call_args.kwargs
        assert call_kwargs['external_context_path'] == context_file


class TestCommandApply:
    """Tests for command_apply function."""

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.load_alt_text_from_json')
    @patch('ada_annotator.cli.DOCXAssembler')
    async def test_apply_docx_success(
        self,
        mock_assembler_class,
        mock_load_json,
        tmp_path,
        mock_logger,
        sample_alt_text_results,
    ):
        """Should successfully apply alt-text to DOCX."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")
        json_file = tmp_path / "alttext.json"
        json_file.write_text("{}")
        output_file = tmp_path / "output.docx"

        # Mock JSON loading - must return dict with structure expected by command_apply
        mock_load_json.return_value = {
            "source_document": str(input_file),
            "alt_text_results": [r.model_dump() for r in sample_alt_text_results],
        }

        # Mock assembler
        mock_assembler = Mock()
        # apply_alt_text should return a status map dict
        mock_assembler.apply_alt_text.return_value = {
            "img_001": "success",
            "img_002": "success",
        }
        mock_assembler_class.return_value = mock_assembler

        # Execute
        result = await command_apply(
            input_path=input_file,
            json_path=json_file,
            output_path=output_file,
            backup=False,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        mock_load_json.assert_called_once_with(json_file)
        mock_assembler_class.assert_called_once()
        mock_assembler.apply_alt_text.assert_called_once()

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.load_alt_text_from_json')
    @patch('ada_annotator.cli.PPTXAssembler')
    async def test_apply_pptx_success(
        self,
        mock_assembler_class,
        mock_load_json,
        tmp_path,
        mock_logger,
        sample_alt_text_results,
    ):
        """Should successfully apply alt-text to PPTX."""
        # Setup
        input_file = tmp_path / "test.pptx"
        input_file.write_text("test")
        json_file = tmp_path / "alttext.json"
        json_file.write_text("{}")
        output_file = tmp_path / "output.pptx"

        # Mock JSON loading - must return dict with structure expected by command_apply
        mock_load_json.return_value = {
            "source_document": str(input_file),
            "alt_text_results": [r.model_dump() for r in sample_alt_text_results],
        }

        # Mock assembler
        mock_assembler = Mock()
        # apply_alt_text should return a status map dict
        mock_assembler.apply_alt_text.return_value = {
            "img_001": "success",
            "img_002": "success",
        }
        mock_assembler_class.return_value = mock_assembler

        # Execute
        result = await command_apply(
            input_path=input_file,
            json_path=json_file,
            output_path=output_file,
            backup=False,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        mock_assembler_class.assert_called_once()

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.load_alt_text_from_json')
    async def test_apply_json_load_error(
        self, mock_load_json, tmp_path, mock_logger
    ):
        """Should return error code when JSON loading fails."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")
        json_file = tmp_path / "alttext.json"
        output_file = tmp_path / "output.docx"

        # Mock JSON loading to raise FileNotFoundError
        mock_load_json.side_effect = FileNotFoundError("JSON file not found")

        # Execute
        result = await command_apply(
            input_path=input_file,
            json_path=json_file,
            output_path=output_file,
            backup=False,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_INPUT_ERROR
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.load_alt_text_from_json')
    @patch('ada_annotator.cli.DOCXAssembler')
    @patch('shutil.copy2')
    async def test_apply_with_backup(
        self,
        mock_shutil_copy,
        mock_assembler_class,
        mock_load_json,
        tmp_path,
        mock_logger,
        sample_alt_text_results,
    ):
        """Should create backup when backup=True."""
        # Setup
        input_file = tmp_path / "test.docx"
        input_file.write_text("test")
        json_file = tmp_path / "alttext.json"
        json_file.write_text("{}")
        output_file = tmp_path / "output.docx"

        # Mock JSON loading
        mock_load_json.return_value = {
            "source_document": str(input_file),
            "alt_text_results": [r.model_dump() for r in sample_alt_text_results],
        }

        # Mock assembler
        mock_assembler = Mock()
        mock_assembler.apply_alt_text.return_value = {
            "img_001": "success",
            "img_002": "success",
        }
        mock_assembler_class.return_value = mock_assembler

        # Execute with backup=True
        result = await command_apply(
            input_path=input_file,
            json_path=json_file,
            output_path=output_file,
            backup=True,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        # Verify backup was created
        mock_shutil_copy.assert_called_once()
        backup_path = input_file.with_stem(f"{input_file.stem}_backup")
        mock_shutil_copy.assert_called_with(input_file, backup_path)

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.load_alt_text_from_json')
    async def test_apply_unsupported_format(
        self, mock_load_json, tmp_path, mock_logger, sample_alt_text_results
    ):
        """Should return error for unsupported file formats."""
        # Setup
        input_file = tmp_path / "test.txt"  # Unsupported format
        input_file.write_text("test")
        json_file = tmp_path / "alttext.json"
        json_file.write_text("{}")
        output_file = tmp_path / "output.txt"

        # Mock JSON loading
        mock_load_json.return_value = {
            "source_document": str(input_file),
            "alt_text_results": [r.model_dump() for r in sample_alt_text_results],
        }

        # Execute
        result = await command_apply(
            input_path=input_file,
            json_path=json_file,
            output_path=output_file,
            backup=False,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_INPUT_ERROR


class TestCommandExtractEdgeCases:
    """Test edge cases and error scenarios for command_extract."""

    @pytest.mark.asyncio
    @patch('ada_annotator.cli.PDFExtractor')
    @patch('ada_annotator.cli.SemanticKernelService')
    @patch('ada_annotator.cli.ContextExtractor')
    @patch('ada_annotator.cli.AltTextGenerator')
    @patch('ada_annotator.cli.save_alt_text_to_json')
    async def test_extract_pdf_with_context(
        self,
        mock_save_json,
        mock_generator_class,
        mock_context_extractor_class,
        mock_ai_service_class,
        mock_extractor_class,
        tmp_path,
        mock_logger,
        sample_images,
        sample_alt_text_results,
    ):
        """Should extract from PDF with context file."""
        # Setup
        input_file = tmp_path / "test.pdf"
        input_file.write_text("test")
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        json_file = output_dir / "alttext.json"
        context_file = tmp_path / "context.txt"
        context_file.write_text("Additional context for images")

        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_images.return_value = sample_images
        mock_extractor_class.return_value = mock_extractor

        # Mock AI generator
        mock_generator = AsyncMock()
        mock_generator.generate_batch_alt_text.return_value = sample_alt_text_results
        mock_generator_class.return_value = mock_generator

        # Execute
        result = await command_extract(
            input_path=input_file,
            output_path=json_file,
            context_path=context_file,
            max_images=None,
            logger=mock_logger,
        )

        # Verify
        assert result == EXIT_SUCCESS
        mock_extractor_class.assert_called_once_with(input_file)
        mock_context_extractor_class.assert_called_once()
        # Verify context file was passed
        call_kwargs = mock_context_extractor_class.call_args.kwargs
        assert call_kwargs["external_context_path"] == context_file


