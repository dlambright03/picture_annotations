"""
Document processing result model.

Contains the complete result of processing a document.
"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class DocumentProcessingResult(BaseModel):
    """
    Complete result of processing a document.

    Tracks all images processed, errors encountered, and resource
    usage for the entire document processing operation.

    Attributes:
        input_file: Path to input document.
        output_file: Path to output document.
        document_type: Type of document (DOCX or PPTX).
        total_images: Total number of images found.
        successful_images: Number of images successfully processed.
        failed_images: Number of images that failed processing.
        images_processed: List of image IDs processed.
        errors: List of error messages encountered.
        total_tokens_used: Total tokens consumed by all API calls.
        estimated_cost_usd: Estimated cost in USD.
        processing_duration_seconds: Total processing time.
        timestamp: When processing completed.
    """

    input_file: Path = Field(..., description="Path to input document")
    output_file: Path = Field(..., description="Path to output document")
    document_type: str = Field(
        ..., description="Type of document (DOCX or PPTX)"
    )
    total_images: int = Field(
        ..., ge=0, description="Total number of images found in document"
    )
    successful_images: int = Field(
        0, ge=0, description="Number of images successfully processed"
    )
    failed_images: int = Field(
        0, ge=0, description="Number of images that failed processing"
    )
    images_processed: list[str] = Field(
        default_factory=list,
        description="List of image IDs that were processed",
    )
    errors: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of errors (image_id, error_message)",
    )
    total_tokens_used: int = Field(
        0, ge=0, description="Total tokens consumed by all API calls"
    )
    estimated_cost_usd: float = Field(
        0.0, ge=0.0, description="Estimated cost in USD"
    )
    processing_duration_seconds: float = Field(
        0.0, ge=0.0, description="Total processing time in seconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When processing completed"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "input_file": "report.docx",
                "output_file": "report_annotated.docx",
                "document_type": "DOCX",
                "total_images": 15,
                "successful_images": 14,
                "failed_images": 1,
                "images_processed": ["img-001", "img-002", "img-003"],
                "errors": [
                    {"image_id": "img-015", "error_message": "API timeout"}
                ],
                "total_tokens_used": 18543,
                "estimated_cost_usd": 0.37,
                "processing_duration_seconds": 45.67,
                "timestamp": "2025-01-18T10:35:22",
            }
        }
