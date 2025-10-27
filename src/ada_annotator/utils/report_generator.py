"""
Report generator for ADA Annotator.

Generates markdown reports summarizing document processing results,
including statistics, successful images, and failures.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from ada_annotator.models import (
    AltTextResult,
    DocumentProcessingResult,
)


class ReportGenerator:
    """
    Generate markdown reports for document processing results.

    Creates comprehensive reports with:
    - Summary statistics (total, success, failed images)
    - Table of processed images with alt-text
    - List of failed images with reasons
    - Token usage and cost estimates
    - Processing duration
    """

    def __init__(self) -> None:
        """Initialize report generator."""
        pass

    def generate_report(
        self,
        result: DocumentProcessingResult,
        alt_text_results: List[AltTextResult],
        output_path: Path,
    ) -> None:
        """
        Generate markdown report for document processing.

        Args:
            result: Complete document processing result.
            alt_text_results: List of alt-text generation results.
            output_path: Path where report will be saved.

        Raises:
            IOError: If unable to write report file.
        """
        report_lines = []

        # Header
        report_lines.append(
            f"# ADA Annotator Processing Report\n"
        )
        report_lines.append(
            f"\n**Generated**: {datetime.now().isoformat()}\n"
        )
        report_lines.append(
            f"**Input File**: `{result.input_file}`\n"
        )
        report_lines.append(
            f"**Output File**: `{result.output_file}`\n"
        )
        report_lines.append(
            f"**Document Type**: {result.document_type}\n\n"
        )

        # Summary Statistics
        report_lines.append("## Summary Statistics\n\n")
        report_lines.extend(self._generate_statistics(result))

        # Successful Images Table
        if alt_text_results:
            report_lines.append("\n## Processed Images\n\n")
            report_lines.extend(
                self._generate_images_table(alt_text_results)
            )

        # Failed Images
        if result.errors:
            report_lines.append("\n## Failed Images\n\n")
            report_lines.extend(self._generate_errors_list(result))

        # Token Usage and Costs
        report_lines.append("\n## Resource Usage\n\n")
        report_lines.extend(self._generate_resource_usage(result))

        # Write report
        try:
            output_path.write_text("".join(report_lines), encoding="utf-8")
        except IOError as e:
            raise IOError(
                f"Failed to write report to {output_path}: {e}"
            ) from e

    def _generate_statistics(
        self,
        result: DocumentProcessingResult
    ) -> List[str]:
        """
        Generate summary statistics section.

        Args:
            result: Document processing result.

        Returns:
            List of markdown lines for statistics.
        """
        lines = []

        success_rate = 0.0
        if result.total_images > 0:
            success_rate = (
                result.successful_images / result.total_images * 100
            )

        lines.append(f"- **Total Images**: {result.total_images}\n")
        lines.append(
            f"- **Successfully Processed**: {result.successful_images}\n"
        )
        lines.append(f"- **Failed**: {result.failed_images}\n")
        lines.append(f"- **Success Rate**: {success_rate:.1f}%\n")
        lines.append(
            f"- **Processing Duration**: "
            f"{result.processing_duration_seconds:.2f}s\n"
        )

        return lines

    def _generate_images_table(
        self,
        alt_text_results: List[AltTextResult]
    ) -> List[str]:
        """
        Generate table of processed images with alt-text.

        Args:
            alt_text_results: List of alt-text generation results.

        Returns:
            List of markdown lines for images table.
        """
        lines = []

        # Table header
        lines.append("| Image ID | Alt-Text | Confidence | Tokens |\n")
        lines.append("|----------|----------|------------|--------|\n")

        # Table rows
        for result in alt_text_results:
            # Truncate alt-text if too long for table
            alt_text = result.alt_text
            if len(alt_text) > 60:
                alt_text = alt_text[:57] + "..."

            lines.append(
                f"| {result.image_id} | {alt_text} | "
                f"{result.confidence_score:.2f} | "
                f"{result.tokens_used} |\n"
            )

        return lines

    def _generate_errors_list(
        self,
        result: DocumentProcessingResult
    ) -> List[str]:
        """
        Generate list of failed images with error reasons.

        Args:
            result: Document processing result.

        Returns:
            List of markdown lines for errors.
        """
        lines = []

        for error in result.errors:
            image_id = error.get("image_id", "unknown")
            error_message = error.get("error_message", "Unknown error")
            page = error.get("page", "N/A")

            lines.append(
                f"- **{image_id}** (Page {page}): {error_message}\n"
            )

        return lines

    def _generate_resource_usage(
        self,
        result: DocumentProcessingResult
    ) -> List[str]:
        """
        Generate resource usage section (tokens and costs).

        Args:
            result: Document processing result.

        Returns:
            List of markdown lines for resource usage.
        """
        lines = []

        lines.append(
            f"- **Total Tokens Used**: {result.total_tokens_used:,}\n"
        )
        lines.append(
            f"- **Estimated Cost**: "
            f"${result.estimated_cost_usd:.4f} USD\n"
        )

        # Average tokens per image
        if result.successful_images > 0:
            avg_tokens = (
                result.total_tokens_used / result.successful_images
            )
            lines.append(
                f"- **Average Tokens per Image**: {avg_tokens:.0f}\n"
            )

        return lines

    def generate_summary(
        self,
        result: DocumentProcessingResult
    ) -> str:
        """
        Generate brief summary string for console output.

        Args:
            result: Document processing result.

        Returns:
            Summary string.
        """
        success_rate = 0.0
        if result.total_images > 0:
            success_rate = (
                result.successful_images / result.total_images * 100
            )

        return (
            f"Processing complete: {result.successful_images}/"
            f"{result.total_images} images ({success_rate:.1f}%) "
            f"in {result.processing_duration_seconds:.2f}s"
        )
