"""Additional CLI tests for validation functions and helpers."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import structlog

from ada_annotator.cli import (
    validate_input_file,
    validate_context_file,
    validate_output_directory,
    generate_output_path,
)


@pytest.fixture
def mock_logger():
    """Create a mock logger with all necessary methods."""
    logger = MagicMock()
    logger.info = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    return logger


class TestValidateInputFile:
    """Tests for validate_input_file function."""

    def test_valid_docx_file(self, tmp_path, mock_logger):
        """Test validation of valid DOCX file."""
        # Arrange
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("fake docx")
        logger = mock_logger

        # Act - should not raise
        validate_input_file(docx_file, logger, debug_mode=False)

        # Assert
        logger.info.assert_called_once()
        assert "input_file_validated" in str(logger.info.call_args)

    def test_valid_pptx_file(self, tmp_path, mock_logger):
        """Test validation of valid PPTX file."""
        # Arrange
        pptx_file = tmp_path / "presentation.pptx"
        pptx_file.write_text("fake pptx")
        logger = mock_logger

        # Act & Assert
        validate_input_file(pptx_file, logger, debug_mode=False)
        logger.info.assert_called_once()

    def test_pdf_file_without_debug_mode(self, tmp_path, mock_logger):
        """Test that PDF is rejected without debug mode."""
        # Arrange
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_text("fake pdf")
        logger = mock_logger

        # Act & Assert
        with pytest.raises(ValueError, match="PDF is only supported with --debug"):
            validate_input_file(pdf_file, logger, debug_mode=False)

        logger.error.assert_called_once()

    def test_pdf_file_with_debug_mode(self, tmp_path, mock_logger):
        """Test that PDF is accepted with debug mode enabled."""
        # Arrange
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_text("fake pdf")
        logger = mock_logger

        # Act & Assert
        validate_input_file(pdf_file, logger, debug_mode=True)
        logger.info.assert_called_once()

    def test_file_not_found(self, tmp_path, mock_logger):
        """Test validation fails when file does not exist."""
        # Arrange
        nonexistent = tmp_path / "nonexistent.docx"
        logger = mock_logger

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            validate_input_file(nonexistent, logger, debug_mode=False)

        logger.error.assert_called_once()

    def test_path_is_directory(self, tmp_path, mock_logger):
        """Test validation fails when path is a directory."""
        # Arrange
        dir_path = tmp_path / "folder"
        dir_path.mkdir()
        logger = mock_logger

        # Act & Assert
        with pytest.raises(ValueError, match="Input path is not a file"):
            validate_input_file(dir_path, logger, debug_mode=False)

    def test_unsupported_extension(self, tmp_path, mock_logger):
        """Test validation fails for unsupported file extension."""
        # Arrange
        txt_file = tmp_path / "document.txt"
        txt_file.write_text("plain text")
        logger = mock_logger

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported file format"):
            validate_input_file(txt_file, logger, debug_mode=False)

    def test_case_insensitive_extension(self, tmp_path, mock_logger):
        """Test that extensions are case-insensitive."""
        # Arrange
        upper_docx = tmp_path / "test.DOCX"
        upper_docx.write_text("fake docx")
        logger = mock_logger

        # Act & Assert - should not raise
        validate_input_file(upper_docx, logger, debug_mode=False)


class TestValidateContextFile:
    """Tests for validate_context_file function."""

    def test_valid_txt_file(self, tmp_path, mock_logger):
        """Test validation of valid TXT context file."""
        # Arrange
        txt_file = tmp_path / "context.txt"
        txt_file.write_text("context information")
        logger = mock_logger

        # Act & Assert
        validate_context_file(txt_file, logger)
        logger.info.assert_called_once()

    def test_valid_md_file(self, tmp_path, mock_logger):
        """Test validation of valid Markdown context file."""
        # Arrange
        md_file = tmp_path / "context.md"
        md_file.write_text("# Context")
        logger = mock_logger

        # Act & Assert
        validate_context_file(md_file, logger)
        logger.info.assert_called_once()

    def test_context_file_not_found(self, tmp_path, mock_logger):
        """Test validation fails when context file does not exist."""
        # Arrange
        nonexistent = tmp_path / "nonexistent.txt"
        logger = mock_logger

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Context file not found"):
            validate_context_file(nonexistent, logger)

    def test_context_path_is_directory(self, tmp_path, mock_logger):
        """Test validation fails when context path is a directory."""
        # Arrange
        dir_path = tmp_path / "folder"
        dir_path.mkdir()
        logger = mock_logger

        # Act & Assert
        with pytest.raises(ValueError, match="Context path is not a file"):
            validate_context_file(dir_path, logger)

    def test_unsupported_context_extension(self, tmp_path, mock_logger):
        """Test validation fails for unsupported context file extension."""
        # Arrange
        docx_file = tmp_path / "context.docx"
        docx_file.write_text("not a text file")
        logger = mock_logger

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported context file format"):
            validate_context_file(docx_file, logger)


class TestValidateOutputDirectory:
    """Tests for validate_output_directory function."""

    def test_writable_output_directory(self, tmp_path, mock_logger):
        """Test validation succeeds for writable output directory."""
        # Arrange
        output_file = tmp_path / "output.docx"
        logger = mock_logger

        # Act & Assert - should not raise
        validate_output_directory(output_file, logger)
        logger.debug.assert_called_once()

    def test_output_directory_does_not_exist(self, tmp_path, mock_logger):
        """Test validation fails when output directory does not exist."""
        # Arrange
        nonexistent_dir = tmp_path / "nonexistent" / "output.docx"
        logger = mock_logger

        # Act & Assert
        with pytest.raises(ValueError, match="Output directory does not exist"):
            validate_output_directory(nonexistent_dir, logger)

    def test_output_directory_not_writable(self, tmp_path, mock_logger):
        """Test validation fails when output directory is not writable."""
        # Arrange
        output_file = tmp_path / "output.docx"
        logger = mock_logger

        # Mock touch to raise PermissionError
        with patch.object(Path, 'touch', side_effect=PermissionError("No write permission")):
            # Act & Assert
            with pytest.raises(ValueError, match="Output directory is not writable"):
                validate_output_directory(output_file, logger)


class TestGenerateOutputPath:
    """Tests for generate_output_path function."""

    def test_generate_docx_output_path(self):
        """Test output path generation for DOCX file."""
        # Arrange
        input_path = Path("document.docx")

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert output_path == Path("document_annotated.docx")
        assert output_path.suffix == ".docx"

    def test_generate_pptx_output_path(self):
        """Test output path generation for PPTX file."""
        # Arrange
        input_path = Path("presentation.pptx")

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert output_path == Path("presentation_annotated.pptx")
        assert output_path.suffix == ".pptx"

    def test_generate_path_with_subdirectory(self):
        """Test output path generation preserves directory structure."""
        # Arrange
        input_path = Path("documents/subfolder/file.docx")

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert output_path == Path("documents/subfolder/file_annotated.docx")
        assert output_path.parent == Path("documents/subfolder")

    def test_generate_path_with_dots_in_filename(self):
        """Test output path generation with dots in filename."""
        # Arrange
        input_path = Path("my.document.v2.docx")

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert output_path == Path("my.document.v2_annotated.docx")

    def test_generate_pdf_output_path(self):
        """Test output path generation for PDF file."""
        # Arrange
        input_path = Path("document.pdf")

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert output_path == Path("document_annotated.pdf")


class TestPathGenerationEdgeCases:
    """Tests for edge cases in path generation."""

    def test_long_filename(self):
        """Test path generation with very long filename."""
        # Arrange
        long_name = "a" * 200 + ".docx"
        input_path = Path(long_name)

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert output_path.suffix == ".docx"
        assert "_annotated" in output_path.stem

    def test_special_characters_in_filename(self):
        """Test path generation with special characters."""
        # Arrange
        input_path = Path("document[2024]-final!.docx")

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert output_path.stem == "document[2024]-final!_annotated"
        assert output_path.suffix == ".docx"

    def test_unicode_in_filename(self, mock_logger):
        """Test path generation with Unicode characters."""
        # Arrange
        input_path = Path("café_présentation_文档.pptx")

        # Act
        output_path = generate_output_path(input_path)

        # Assert
        assert "_annotated" in output_path.stem
        assert output_path.suffix == ".pptx"
