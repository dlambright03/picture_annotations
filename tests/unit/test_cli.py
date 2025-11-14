"""Unit tests for CLI argument parsing and validation."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

from ada_annotator.cli import (
    create_argument_parser,
    validate_input_file,
    validate_context_file,
    validate_output_directory,
    generate_output_path,
    main,
)
from ada_annotator.exceptions import EXIT_SUCCESS, EXIT_INPUT_ERROR


class TestArgumentParser:
    """Tests for CLI argument parser configuration."""

    def test_parser_creation(self) -> None:
        """Test that argument parser is created successfully."""
        parser = create_argument_parser()
        assert parser is not None
        assert parser.prog == "ada-annotator"

    def test_required_input_argument(self) -> None:
        """Test that input file is a required argument."""
        parser = create_argument_parser()

        # Should fail without subcommand - suppress argparse stderr output
        with patch('sys.stderr'):
            with pytest.raises(SystemExit):
                parser.parse_args([])

        # Should succeed with extract subcommand and input
        args = parser.parse_args(["extract", "test.docx"])
        assert args.extract_input == "test.docx"
        assert args.command == "extract"

    def test_optional_output_argument(self) -> None:
        """Test --output argument is parsed correctly."""
        parser = create_argument_parser()
        args = parser.parse_args(["extract", "test.docx", "--output", "output.json"])

        assert args.output == "output.json"

    def test_optional_context_argument(self) -> None:
        """Test --context argument is parsed correctly."""
        parser = create_argument_parser()
        args = parser.parse_args(["extract", "test.docx", "--context", "context.txt"])

        assert args.context == "context.txt"

    def test_backup_flag_on_apply(self) -> None:
        """Test --backup flag is parsed correctly on apply command."""
        parser = create_argument_parser()
        args = parser.parse_args(["apply", "test.docx", "alttext.json", "--backup"])

        assert args.backup is True

    def test_extract_command_parsed(self) -> None:
        """Test extract command is parsed correctly."""
        parser = create_argument_parser()
        args = parser.parse_args(["extract", "test.docx"])

        assert args.command == "extract"
        assert args.extract_input == "test.docx"

    def test_apply_command_parsed(self) -> None:
        """Test apply command is parsed correctly."""
        parser = create_argument_parser()
        args = parser.parse_args(["apply", "test.docx", "alttext.json"])

        assert args.command == "apply"
        assert args.apply_input == "test.docx"
        assert args.alttext == "alttext.json"

    def test_log_level_argument(self) -> None:
        """Test --log-level argument with valid choices."""
        parser = create_argument_parser()
        args = parser.parse_args(["extract", "test.docx", "--log-level", "DEBUG"])

        assert args.log_level == "DEBUG"

    def test_invalid_log_level(self) -> None:
        """Test that invalid log level is rejected."""
        parser = create_argument_parser()

        with patch('sys.stderr'):
            with pytest.raises(SystemExit):
                parser.parse_args(["extract", "test.docx", "--log-level", "INVALID"])

    def test_max_images_argument(self) -> None:
        """Test --max-images argument is parsed correctly."""
        parser = create_argument_parser()
        args = parser.parse_args(["extract", "test.docx", "--max-images", "10"])

        assert args.max_images == 10

    def test_short_flags_extract(self) -> None:
        """Test that short flags work correctly on extract command."""
        parser = create_argument_parser()
        args = parser.parse_args([
            "extract",
            "test.docx",
            "-o", "output.json",
            "-c", "context.txt",
        ])

        assert args.output == "output.json"
        assert args.context == "context.txt"

    def test_short_flags_apply(self) -> None:
        """Test that short flags work correctly on apply command."""
        parser = create_argument_parser()
        args = parser.parse_args([
            "apply",
            "test.docx",
            "alttext.json",
            "-o", "output.docx",
        ])

        assert args.output == "output.docx"


class TestInputFileValidation:
    """Tests for input file validation."""

    def test_validate_existing_docx_file(self, tmp_path: Path) -> None:
        """Test validation passes for existing DOCX file."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        # Create test file
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        # Should not raise exception
        validate_input_file(test_file, logger)

    def test_validate_existing_pptx_file(self, tmp_path: Path) -> None:
        """Test validation passes for existing PPTX file."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        test_file = tmp_path / "test.pptx"
        test_file.write_text("test content")

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        validate_input_file(test_file, logger)

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        """Test validation fails for nonexistent file."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        test_file = tmp_path / "nonexistent.docx"

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        with pytest.raises(FileNotFoundError, match="not found"):
            validate_input_file(test_file, logger)

    def test_validate_unsupported_format(self, tmp_path: Path) -> None:
        """Test validation fails for unsupported file format."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        with pytest.raises(ValueError, match="Unsupported file format"):
            validate_input_file(test_file, logger)

    def test_validate_directory_instead_of_file(self, tmp_path: Path) -> None:
        """Test validation fails when path is a directory."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        with pytest.raises(ValueError, match="not a file"):
            validate_input_file(tmp_path, logger)


class TestContextFileValidation:
    """Tests for context file validation."""

    def test_validate_existing_txt_file(self, tmp_path: Path) -> None:
        """Test validation passes for existing TXT file."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        test_file = tmp_path / "context.txt"
        test_file.write_text("context content")

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        validate_context_file(test_file, logger)

    def test_validate_existing_md_file(self, tmp_path: Path) -> None:
        """Test validation passes for existing MD file."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        test_file = tmp_path / "context.md"
        test_file.write_text("# Context")

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        validate_context_file(test_file, logger)

    def test_validate_nonexistent_context_file(self, tmp_path: Path) -> None:
        """Test validation fails for nonexistent context file."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        test_file = tmp_path / "nonexistent.txt"

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        with pytest.raises(FileNotFoundError, match="not found"):
            validate_context_file(test_file, logger)

    def test_validate_unsupported_context_format(self, tmp_path: Path) -> None:
        """Test validation fails for unsupported context format."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        test_file = tmp_path / "context.docx"
        test_file.write_text("context")

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        with pytest.raises(ValueError, match="Unsupported context file format"):
            validate_context_file(test_file, logger)


class TestOutputDirectoryValidation:
    """Tests for output directory validation."""

    def test_validate_writable_directory(self, tmp_path: Path) -> None:
        """Test validation passes for writable directory."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        output_file = tmp_path / "output.docx"

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        validate_output_directory(output_file, logger)

    def test_validate_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test validation fails for nonexistent directory."""
        from ada_annotator.utils.logging import setup_logging, get_logger

        output_file = tmp_path / "nonexistent" / "output.docx"

        setup_logging(tmp_path / "test.log", "INFO", False)
        logger = get_logger(__name__)

        with pytest.raises(ValueError, match="does not exist"):
            validate_output_directory(output_file, logger)


class TestOutputPathGeneration:
    """Tests for output path generation."""

    def test_generate_output_path_docx(self) -> None:
        """Test output path generation for DOCX files."""
        input_path = Path("document.docx")
        output_path = generate_output_path(input_path)

        assert output_path == Path("document_annotated.docx")

    def test_generate_output_path_pptx(self) -> None:
        """Test output path generation for PPTX files."""
        input_path = Path("presentation.pptx")
        output_path = generate_output_path(input_path)

        assert output_path == Path("presentation_annotated.pptx")

    def test_generate_output_path_with_directory(self) -> None:
        """Test output path generation preserves directory."""
        input_path = Path("docs/document.docx")
        output_path = generate_output_path(input_path)

        assert output_path == Path("docs/document_annotated.docx")


class TestCLIMain:
    """Tests for CLI main function."""

    @patch('ada_annotator.cli.asyncio.run')
    @patch('ada_annotator.cli.command_extract')
    def test_main_with_valid_input(self, mock_extract, mock_async_run, tmp_path: Path) -> None:
        """Test main function with valid input file."""
        # Create test file
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")

        # Mock successful extraction
        mock_async_run.return_value = EXIT_SUCCESS

        exit_code = main(["extract", str(test_file)])

        assert exit_code == EXIT_SUCCESS
        mock_async_run.assert_called_once()
        mock_extract.assert_called_once()

    def test_main_with_nonexistent_file(self, tmp_path: Path) -> None:
        """Test main function with nonexistent input file."""
        test_file = tmp_path / "nonexistent.docx"

        exit_code = main(["extract", str(test_file)])

        assert exit_code == EXIT_INPUT_ERROR

    def test_main_with_unsupported_format(self, tmp_path: Path) -> None:
        """Test main function with unsupported file format."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        exit_code = main(["extract", str(test_file)])

        assert exit_code == EXIT_INPUT_ERROR

    @patch('ada_annotator.cli.asyncio.run')
    @patch('ada_annotator.cli.command_extract')
    def test_main_with_output_argument(self, mock_extract, mock_async_run, tmp_path: Path) -> None:
        """Test main function with custom output path."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")
        output_file = tmp_path / "output.json"

        # Mock successful extraction
        mock_async_run.return_value = EXIT_SUCCESS

        exit_code = main(["extract", str(test_file), "--output", str(output_file)])

        assert exit_code == EXIT_SUCCESS
        mock_async_run.assert_called_once()
        mock_extract.assert_called_once()

    @patch('ada_annotator.cli.asyncio.run')
    @patch('ada_annotator.cli.command_extract')
    def test_main_with_context_file(self, mock_extract, mock_async_run, tmp_path: Path) -> None:
        """Test main function with context file."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")
        context_file = tmp_path / "context.txt"
        context_file.write_text("context")

        # Mock successful extraction
        mock_async_run.return_value = EXIT_SUCCESS

        exit_code = main(["extract", str(test_file), "--context", str(context_file)])

        assert exit_code == EXIT_SUCCESS
        mock_async_run.assert_called_once()
        mock_extract.assert_called_once()

    def test_main_with_invalid_context_file(self, tmp_path: Path) -> None:
        """Test main function with invalid context file."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")
        context_file = tmp_path / "nonexistent.txt"

        exit_code = main(["extract", str(test_file), "--context", str(context_file)])

        assert exit_code == EXIT_INPUT_ERROR

    def test_main_with_max_images(self, tmp_path: Path) -> None:
        """Test main function with max-images limit."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")

        # Should fail with invalid file but parser should accept the argument
        exit_code = main(["extract", str(test_file), "--max-images", "5"])

        # Will fail due to invalid DOCX, but that's expected
        assert exit_code != EXIT_SUCCESS  # File isn't a real DOCX

    def test_main_with_log_level(self, tmp_path: Path) -> None:
        """Test main function with log level."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")

        # Should fail with invalid file but parser should accept the argument
        exit_code = main(["extract", str(test_file), "--log-level", "DEBUG"])

        # Will fail due to invalid DOCX, but that's expected
        assert exit_code != EXIT_SUCCESS  # File isn't a real DOCX
