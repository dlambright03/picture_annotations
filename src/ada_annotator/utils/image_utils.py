"""
Image utility functions for ADA Annotator.

Provides image conversion, validation, and format detection functions.
"""

import base64
from pathlib import Path

from PIL import Image

from ada_annotator.utils.logging import get_logger

logger = get_logger(__name__)


def analyze_image_content(image_data: bytes) -> dict:
    """
    Analyze image to detect potential issues like transparency or low content.

    Args:
        image_data: Raw image binary data

    Returns:
        Dict with analysis results including:
        - is_mostly_transparent: bool
        - is_very_small: bool
        - has_alpha: bool
        - unique_colors: int

    Example:
        >>> with open("image.png", "rb") as f:
        ...     data = f.read()
        >>> analysis = analyze_image_content(data)
        >>> if analysis['is_mostly_transparent']:
        ...     print("Image is mostly transparent")
    """
    from io import BytesIO

    try:
        img = Image.open(BytesIO(image_data))

        analysis = {
            "is_mostly_transparent": False,
            "is_very_small": False,
            "has_alpha": False,
            "unique_colors": 0,
            "width": img.width,
            "height": img.height,
        }

        # Check if very small
        if img.width * img.height < 100:  # Less than 100 pixels total
            analysis["is_very_small"] = True

        # Check for alpha channel
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            analysis["has_alpha"] = True

            # Convert to RGBA to analyze transparency
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Count transparent pixels
            pixels = list(img.getdata())
            transparent_count = sum(1 for p in pixels if len(p) == 4 and p[3] < 10)
            transparency_ratio = transparent_count / len(pixels)

            if transparency_ratio > 0.9:  # More than 90% transparent
                analysis["is_mostly_transparent"] = True

        # Estimate unique colors (sample for performance)
        if img.mode in ("RGB", "RGBA"):
            # Sample up to 1000 pixels
            sample_size = min(1000, img.width * img.height)
            step = max(1, (img.width * img.height) // sample_size)
            pixels = list(img.getdata())[::step]
            unique = len(set(pixels))
            analysis["unique_colors"] = unique

        return analysis

    except Exception as e:
        logger.warning(f"Failed to analyze image content: {e}")
        return {
            "is_mostly_transparent": False,
            "is_very_small": False,
            "has_alpha": False,
            "unique_colors": 0,
        }


def convert_image_bytes_to_base64(
    image_data: bytes, include_prefix: bool = False, image_format: str = "jpeg"
) -> str:
    """
    Convert image binary data to base64 encoded string.

    Args:
        image_data: Raw image binary data
        include_prefix: If True, includes data URI prefix
                       (e.g., "data:image/jpeg;base64,")
        image_format: Image format for prefix (e.g., "jpeg", "png")

    Returns:
        Base64 encoded string representation of the image

    Example:
        >>> with open("image.jpg", "rb") as f:
        ...     data = f.read()
        >>> base64_str = convert_image_bytes_to_base64(data)
    """
    # Encode to base64
    base64_encoded = base64.b64encode(image_data).decode("utf-8")

    if include_prefix:
        # Normalize format name
        fmt = image_format.lower()
        if fmt in ["jpg", "jpeg"]:
            fmt = "jpeg"
        return f"data:image/{fmt};base64,{base64_encoded}"

    return base64_encoded


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
