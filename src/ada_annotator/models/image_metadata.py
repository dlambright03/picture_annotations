"""
Image metadata model for extracted images.

Contains all information about an image including position, format,
and existing alt-text if present.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    """
    Metadata for an extracted image from a document.

    Attributes:
        image_id: Unique identifier for the image.
        filename: Original or generated filename.
        format: Image format (JPEG, PNG, GIF, BMP).
        size_bytes: Size of image in bytes.
        width_pixels: Width in pixels.
        height_pixels: Height in pixels.
        page_number: Page or slide number (1-indexed), None for DOCX.
        position: Dictionary containing position metadata.
        existing_alt_text: Pre-existing alt-text if present.
    """

    image_id: str = Field(..., description="Unique identifier for the image")
    filename: str = Field(..., description="Original or generated filename")
    format: Literal["JPEG", "PNG", "GIF", "BMP"] = Field(
        ..., description="Image format"
    )
    size_bytes: int = Field(..., gt=0, description="Size of image in bytes")
    width_pixels: int = Field(..., gt=0, description="Width in pixels")
    height_pixels: int = Field(..., gt=0, description="Height in pixels")
    page_number: int | None = Field(
        None, gt=0, description="Page or slide number (1-indexed)"
    )
    position: dict = Field(
        default_factory=dict, description="Position metadata (format-specific)"
    )
    existing_alt_text: str | None = Field(
        None, description="Pre-existing alt-text if present"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "image_id": "slide1_img0",
                "filename": "slide1_image0.jpeg",
                "format": "JPEG",
                "size_bytes": 45678,
                "width_pixels": 800,
                "height_pixels": 600,
                "page_number": 1,
                "position": {
                    "x": 100,
                    "y": 200,
                    "width": 800,
                    "height": 600,
                    "anchor_type": "floating",
                },
                "existing_alt_text": None,
            }
        }
