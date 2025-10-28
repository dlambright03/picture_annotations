"""
Image utility functions for ADA Annotator.

Provides image conversion, validation, and format detection functions.
"""

import base64
from pathlib import Path

from PIL import Image

from ada_annotator.utils.logging import get_logger

logger = get_logger(__name__)


def convert_image_to_base64(
    image_path: str | Path, include_prefix: bool = False
) -> str:
    """
    Convert an image file to base64 encoded string.

    Args:
        image_path: Path to the image file
        include_prefix: If True, includes data URI prefix
                       (e.g., "data:image/png;base64,")

    Returns:
        Base64 encoded string representation of the image

    Raises:
        FileNotFoundError: If image file does not exist
        ValueError: If file is not a valid image
        IOError: If file cannot be read

    Example:
        >>> base64_str = convert_image_to_base64("image.png")
        >>> # With data URI prefix
        >>> data_uri = convert_image_to_base64("image.png",
        ...                                     include_prefix=True)
    """
    image_path = Path(image_path)

    if not image_path.exists():
        logger.error(f"Image file not found: {image_path}")
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        # Validate it's a real image by opening with PIL
        with Image.open(image_path) as img:
            img.verify()

        # Read the file as binary
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()

        # Encode to base64
        base64_encoded = base64.b64encode(image_data).decode("utf-8")

        if include_prefix:
            # Detect image format for data URI
            img_format = get_image_format(image_path).lower()
            # Normalize JPEG variants
            if img_format in ["jpg", "jpeg"]:
                img_format = "jpeg"
            return f"data:image/{img_format};base64,{base64_encoded}"

        return base64_encoded

    except Exception as e:
        logger.error(f"Failed to convert image to base64: {image_path} - {e}")
        raise ValueError(
            f"Invalid image file or cannot be read: {image_path}"
        ) from e


def get_image_format(image_path: str | Path) -> str:
    """
    Detect the format of an image file.

    Args:
        image_path: Path to the image file

    Returns:
        Image format as string (e.g., "PNG", "JPEG", "BMP")

    Raises:
        FileNotFoundError: If image file does not exist
        ValueError: If file is not a valid image

    Example:
        >>> fmt = get_image_format("photo.jpg")
        >>> print(fmt)  # Output: "JPEG"
    """
    image_path = Path(image_path)

    if not image_path.exists():
        logger.error(f"Image file not found: {image_path}")
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        with Image.open(image_path) as img:
            return img.format if img.format else "UNKNOWN"
    except Exception as e:
        logger.error(f"Failed to detect image format: {image_path} - {e}")
        raise ValueError(f"Invalid image file: {image_path}") from e


def validate_image_file(image_path: str | Path) -> bool:
    """
    Validate that a file is a valid image.

    Args:
        image_path: Path to the file to validate

    Returns:
        True if file is a valid image, False otherwise

    Example:
        >>> if validate_image_file("photo.png"):
        ...     print("Valid image")
        ... else:
        ...     print("Invalid image")
    """
    image_path = Path(image_path)

    if not image_path.exists():
        logger.warning(f"Image file not found: {image_path}")
        return False

    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception as e:
        logger.warning(f"Invalid image file: {image_path} - {e}")
        return False
