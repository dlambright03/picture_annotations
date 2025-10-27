"""
Tests for report generator module.

Tests markdown report generation, statistics, and formatting.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ada_annotator.models import AltTextResult, DocumentProcessingResult
from ada_annotator.utils import ReportGenerator


@pytest.fixture
def report_generator() -> ReportGenerator:
    """Create report generator instance."""
    return ReportGenerator()


@pytest.fixture
def sample_processing_result() -> DocumentProcessingResult:
    """Create sample processing result."""
    return DocumentProcessingResult(
        input_file=Path("test.docx"),
        output_file=Path("test_output.docx"),
        document_type="DOCX",
        total_images=10,
        successful_images=8,
        failed_images=2,
        images_processed=["img-001", "img-002", "img-003"],
        errors=[
            {
                "image_id": "img-004",
                "error_message": "API timeout",
                "page": "5",
            },
            {
                "image_id": "img-005",
                "error_message": "Invalid image format",
                "page": "7",
            },
        ],
        total_tokens_used=15000,
        estimated_cost_usd=0.30,
        processing_duration_seconds=45.5,
    )


@pytest.fixture
def sample_alt_text_results() -> list:
    """Create sample alt-text results."""
    return [
        AltTextResult(
            image_id="img-001",
            alt_text="A diagram showing the water cycle",
            confidence_score=0.92,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=500,
            processing_time_seconds=2.3,
        ),
        AltTextResult(
            image_id="img-002",
            alt_text="Chart displaying quarterly sales data",
            confidence_score=0.88,
            validation_passed=True,
            validation_warnings=["Slightly short description"],
            tokens_used=450,
            processing_time_seconds=2.1,
        ),
        AltTextResult(
            image_id="img-003",
            alt_text=(
                "Very long description that needs to be truncated "
                "in the table to maintain readability and formatting"
            ),
            confidence_score=0.95,
            validation_passed=True,
            validation_warnings=[],
            tokens_used=600,
            processing_time_seconds=2.5,
        ),
    ]


def test_report_generator_initialization(report_generator):
    """Test report generator initialization."""
    assert report_generator is not None


def test_generate_report_creates_file(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
    tmp_path,
):
    """Test that generate_report creates markdown file."""
    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        sample_processing_result,
        sample_alt_text_results,
        output_path,
    )

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert len(content) > 0


def test_generate_report_contains_header(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
    tmp_path,
):
    """Test report contains proper header."""
    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        sample_processing_result,
        sample_alt_text_results,
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")
    assert "# ADA Annotator Processing Report" in content
    assert "**Input File**" in content
    assert "test.docx" in content
    assert "**Output File**" in content
    assert "test_output.docx" in content


def test_generate_report_contains_statistics(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
    tmp_path,
):
    """Test report contains summary statistics."""
    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        sample_processing_result,
        sample_alt_text_results,
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")
    assert "## Summary Statistics" in content
    assert "**Total Images**: 10" in content
    assert "**Successfully Processed**: 8" in content
    assert "**Failed**: 2" in content
    assert "**Success Rate**: 80.0%" in content
    assert "**Processing Duration**: 45.50s" in content


def test_generate_report_contains_images_table(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
    tmp_path,
):
    """Test report contains processed images table."""
    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        sample_processing_result,
        sample_alt_text_results,
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")
    assert "## Processed Images" in content
    assert "| Image ID | Alt-Text | Confidence | Tokens |" in content
    assert "img-001" in content
    assert "water cycle" in content
    assert "0.92" in content


def test_generate_report_truncates_long_alt_text(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
    tmp_path,
):
    """Test that long alt-text is truncated in table."""
    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        sample_processing_result,
        sample_alt_text_results,
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")
    # Long alt-text should be truncated with ...
    assert "..." in content
    # But full text should not appear
    full_text = sample_alt_text_results[2].alt_text
    assert full_text not in content


def test_generate_report_contains_errors(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
    tmp_path,
):
    """Test report contains failed images section."""
    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        sample_processing_result,
        sample_alt_text_results,
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")
    assert "## Failed Images" in content
    assert "img-004" in content
    assert "API timeout" in content
    assert "Page 5" in content
    assert "img-005" in content
    assert "Invalid image format" in content
    assert "Page 7" in content


def test_generate_report_contains_resource_usage(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
    tmp_path,
):
    """Test report contains resource usage section."""
    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        sample_processing_result,
        sample_alt_text_results,
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")
    assert "## Resource Usage" in content
    assert "**Total Tokens Used**: 15,000" in content
    assert "**Estimated Cost**: $0.3000 USD" in content
    assert "**Average Tokens per Image**" in content


def test_generate_report_handles_no_images(
    report_generator, tmp_path
):
    """Test report generation with no processed images."""
    result = DocumentProcessingResult(
        input_file=Path("empty.docx"),
        output_file=Path("empty_output.docx"),
        document_type="DOCX",
        total_images=0,
        successful_images=0,
        failed_images=0,
        images_processed=[],
        errors=[],
        total_tokens_used=0,
        estimated_cost_usd=0.0,
        processing_duration_seconds=1.0,
    )

    output_path = tmp_path / "report.md"

    report_generator.generate_report(result, [], output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "**Total Images**: 0" in content
    assert "## Processed Images" not in content


def test_generate_report_handles_no_errors(
    report_generator, sample_alt_text_results, tmp_path
):
    """Test report generation with no errors."""
    result = DocumentProcessingResult(
        input_file=Path("test.docx"),
        output_file=Path("test_output.docx"),
        document_type="DOCX",
        total_images=3,
        successful_images=3,
        failed_images=0,
        images_processed=["img-001", "img-002", "img-003"],
        errors=[],
        total_tokens_used=1550,
        estimated_cost_usd=0.03,
        processing_duration_seconds=7.0,
    )

    output_path = tmp_path / "report.md"

    report_generator.generate_report(
        result, sample_alt_text_results, output_path
    )

    content = output_path.read_text(encoding="utf-8")
    assert "## Failed Images" not in content
    assert "**Success Rate**: 100.0%" in content


def test_generate_report_io_error(
    report_generator,
    sample_processing_result,
    sample_alt_text_results,
):
    """Test report generation handles IO errors."""
    # Use invalid path
    invalid_path = Path("/invalid/path/report.md")

    with pytest.raises(IOError):
        report_generator.generate_report(
            sample_processing_result,
            sample_alt_text_results,
            invalid_path,
        )


def test_generate_summary(report_generator, sample_processing_result):
    """Test summary string generation."""
    summary = report_generator.generate_summary(
        sample_processing_result
    )

    assert "8/10 images" in summary
    assert "80.0%" in summary
    assert "45.50s" in summary


def test_generate_summary_zero_images(report_generator):
    """Test summary with zero images."""
    result = DocumentProcessingResult(
        input_file=Path("empty.docx"),
        output_file=Path("empty_output.docx"),
        document_type="DOCX",
        total_images=0,
        successful_images=0,
        failed_images=0,
        images_processed=[],
        errors=[],
        total_tokens_used=0,
        estimated_cost_usd=0.0,
        processing_duration_seconds=1.0,
    )

    summary = report_generator.generate_summary(result)

    assert "0/0 images" in summary
