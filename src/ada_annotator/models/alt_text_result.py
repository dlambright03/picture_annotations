"""
Alt-text result model for AI-generated descriptions.

Contains the result of generating alt-text for a single image.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class AltTextResult(BaseModel):
    """
    Result of generating alt-text for an image.

    Contains the AI-generated alt-text, validation results, and
    metadata about the generation process.

    Attributes:
        image_id: Unique identifier for the image.
        alt_text: Generated alternative text description.
        confidence_score: AI confidence (0.0-1.0).
        validation_passed: Whether validation checks passed.
        validation_warnings: List of validation warnings.
        tokens_used: Number of tokens consumed by API call.
        processing_time_seconds: Time taken to generate alt-text.
        timestamp: When the alt-text was generated.
    """

    image_id: str = Field(..., description="Unique identifier for the image")
    alt_text: str = Field(
        ...,
        min_length=1,
        max_length=250,
        description="Generated alternative text (1-250 chars)",
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="AI confidence score (0.0-1.0)"
    )
    validation_passed: bool = Field(
        ..., description="Whether validation checks passed"
    )
    validation_warnings: list[str] = Field(
        default_factory=list, description="List of validation warnings"
    )
    tokens_used: int = Field(
        ..., ge=0, description="Number of tokens consumed by API call"
    )
    processing_time_seconds: float = Field(
        ..., ge=0.0, description="Time taken to generate alt-text"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the alt-text was generated",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "image_id": "img-001",
                "alt_text": (
                    "Diagram of a mitochondrion showing inner and "
                    "outer membranes with cristae folds"
                ),
                "confidence_score": 0.92,
                "validation_passed": True,
                "validation_warnings": [],
                "tokens_used": 1247,
                "processing_time_seconds": 2.34,
                "timestamp": "2025-01-18T10:30:45",
            }
        }
