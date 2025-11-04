"""
Alt-text generation orchestrator.

Coordinates the complete alt-text generation workflow by integrating
context extraction, AI service calls, validation, and result construction.
"""

import re
import time
from collections.abc import Callable

from ada_annotator.config import Settings
from ada_annotator.exceptions import APIError
from ada_annotator.models import AltTextResult, ContextData, ImageMetadata
from ada_annotator.utils.logging import get_logger

logger = get_logger(__name__)


class AltTextGenerator:
    """
    Orchestrates alt-text generation for images.

    Integrates context extraction, AI service calls, validation,
    and result construction into a complete workflow.

    Attributes:
        settings: Application settings.
        ai_service: AI service for generating alt-text.
        context_extractor: Context extractor for images.
    """

    # Validation constants
    MIN_LENGTH = 10
    MAX_LENGTH = 350
    PREFERRED_MIN = 80
    PREFERRED_MAX = 280

    # Forbidden phrases in alt-text
    FORBIDDEN_PHRASES = [
        "image of",
        "picture of",
        "graphic showing",
        "photo of",
        "screenshot of",
        "diagram showing",
        "illustration of",
    ]

    # Patterns that indicate poor quality alt-text
    POOR_QUALITY_PATTERNS = [
        r"^[a-z0-9_\-\.]+$",  # Looks like a filename
        r"^(fig|figure|img|image)[_\s]?\d+",  # Figure numbers
        r"^\d+[a-z]?_[a-z]+_\d+",  # Pattern like "18_p_844"
    ]

    # Vague descriptions to avoid
    VAGUE_DESCRIPTIONS = [
        "a diagram",
        "a chart",
        "a graph",
        "a table",
        "an image",
        "a picture",
        "a figure",
        "content",
        "decorative",
    ]

    # Cost estimates (Azure OpenAI GPT-4o pricing per 1M tokens)
    INPUT_COST_PER_TOKEN = 2.50 / 1_000_000
    OUTPUT_COST_PER_TOKEN = 10.00 / 1_000_000

    def __init__(
        self,
        settings: Settings,
        ai_service,
        context_extractor,
    ):
        """
        Initialize the alt-text generator.

        Args:
            settings: Application settings.
            ai_service: AI service instance (SemanticKernelService).
            context_extractor: Context extractor instance.
        """
        self.settings = settings
        self.ai_service = ai_service
        self.context_extractor = context_extractor

        logger.info("AltTextGenerator initialized")

    async def generate_for_image(
        self, image_metadata: ImageMetadata
    ) -> AltTextResult:
        """
        Generate alt-text for a single image.

        Args:
            image_metadata: Metadata about the image.

        Returns:
            AltTextResult with generated alt-text and metadata.

        Raises:
            APIError: If AI service fails after retries.
        """
        start_time = time.time()

        logger.info(f"Generating alt-text for image {image_metadata.image_id}")

        # Extract context for the image
        try:
            context_data = self.context_extractor.extract_context_for_image(
                image_metadata
            )
            merged_context = context_data.get_merged_context()
        except Exception as e:
            logger.warning(
                f"Context extraction failed for {image_metadata.image_id}: "
                f"{e}. Using minimal context."
            )
            # Fallback to minimal context
            context_data = ContextData(
                document_context=f"Document containing {image_metadata.format} image",
                local_context="No surrounding text available.",
            )
            merged_context = context_data.get_merged_context()

        # Generate alt-text using AI service
        try:
            raw_alt_text = await self.ai_service.generate_alt_text(
                image_metadata, merged_context
            )
        except APIError:
            # Re-raise API errors (let caller handle)
            raise

        # Auto-correct alt-text and check if decorative
        alt_text, is_decorative = self._auto_correct_alt_text(raw_alt_text)

        # Validate alt-text (skip validation if decorative)
        if is_decorative:
            validation_passed = True
            warnings = []
        else:
            validation_passed, warnings = self._validate_alt_text(alt_text)

        # Calculate confidence score based on quality factors
        confidence_score = self._calculate_confidence_score(
            alt_text, 
            is_decorative, 
            validation_passed, 
            warnings,
            len(merged_context) > 0
        )

        # Track processing time
        processing_time = time.time() - start_time

        # Estimate token usage (rough approximation)
        # Real implementation would get this from AI response
        estimated_input_tokens = len(merged_context) // 4
        estimated_output_tokens = len(alt_text) // 4
        total_tokens = estimated_input_tokens + estimated_output_tokens

        # Create result object
        result = AltTextResult(
            image_id=image_metadata.image_id,
            alt_text=alt_text,
            is_decorative=is_decorative,
            confidence_score=confidence_score,
            validation_passed=validation_passed,
            validation_warnings=warnings,
            tokens_used=total_tokens,
            processing_time_seconds=round(processing_time, 3),
        )

        if is_decorative:
            logger.info(
                f"Image {image_metadata.image_id} marked as DECORATIVE"
            )
        else:
            logger.info(
                f"Generated alt-text for {image_metadata.image_id}: "
                f"{len(alt_text)} chars, {total_tokens} tokens, "
                f"{processing_time:.2f}s"
            )

        return result

    async def generate_for_multiple_images(
        self,
        images: list[ImageMetadata],
        continue_on_error: bool = False,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[AltTextResult]:
        """
        Generate alt-text for multiple images.

        Args:
            images: List of image metadata objects.
            continue_on_error: If True, continue processing after errors.
            progress_callback: Optional callback for progress updates.

        Returns:
            List of AltTextResult objects for successful generations.
        """
        results = []
        total = len(images)

        logger.info(f"Generating alt-text for {total} images")

        for index, image_meta in enumerate(images, start=1):
            try:
                result = await self.generate_for_image(image_meta)
                results.append(result)

                if progress_callback:
                    progress_callback(index, total)

            except APIError as e:
                logger.error(
                    f"Failed to generate alt-text for "
                    f"{image_meta.image_id}: {e}"
                )
                if not continue_on_error:
                    raise
                # Continue to next image

        logger.info(
            f"Completed batch: {len(results)}/{total} images successful"
        )

        return results

    def _validate_alt_text(self, alt_text: str) -> tuple[bool, list[str]]:
        """
        Validate alt-text against quality rules.

        Args:
            alt_text: Generated alt-text to validate.

        Returns:
            Tuple of (passed, warnings) where passed is bool
            and warnings is list of warning messages.
        """
        warnings = []
        passed = True

        # Check minimum length
        if len(alt_text) < self.MIN_LENGTH:
            warnings.append(
                f"Alt-text too short (minimum {self.MIN_LENGTH} chars)"
            )
            passed = False

        # Check maximum length
        if len(alt_text) > self.MAX_LENGTH:
            warnings.append(
                f"Alt-text too long (maximum {self.MAX_LENGTH} chars)"
            )
            passed = False

        # Warn if outside preferred range
        if self.MIN_LENGTH <= len(alt_text) < self.PREFERRED_MIN:
            warnings.append(
                f"Alt-text is short (preferred {self.PREFERRED_MIN}+ chars)"
            )

        if self.PREFERRED_MAX < len(alt_text) <= self.MAX_LENGTH:
            warnings.append(
                f"Alt-text is long (preferred {self.PREFERRED_MAX}- chars)"
            )

        # Check for forbidden phrases
        alt_text_lower = alt_text.lower()
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in alt_text_lower:
                warnings.append(
                    f"Alt-text contains forbidden phrase: '{phrase}'"
                )
                passed = False

        # Check for poor quality patterns (looks like filename)
        for pattern in self.POOR_QUALITY_PATTERNS:
            if re.search(pattern, alt_text, re.IGNORECASE):
                warnings.append(
                    "Alt-text looks like a filename or code - needs descriptive text"
                )
                passed = False
                break

        # Check for vague descriptions (if the entire text is just a vague term)
        alt_text_stripped = alt_text.strip().rstrip(".")
        if alt_text_stripped.lower() in self.VAGUE_DESCRIPTIONS:
            warnings.append(
                f"Alt-text is too vague: '{alt_text_stripped}'"
            )
            passed = False

        # Check capitalization
        if alt_text and not alt_text[0].isupper():
            warnings.append("Alt-text should start with uppercase letter")

        # Check for ending punctuation (period expected)
        if not alt_text.endswith("."):
            warnings.append("Alt-text should end with a period")

        return passed, warnings

    def _auto_correct_alt_text(self, alt_text: str) -> tuple[str, bool]:
        """
        Apply automatic corrections to alt-text and detect decorative images.

        Args:
            alt_text: Raw alt-text from AI.

        Returns:
            tuple: (corrected alt-text, is_decorative flag)
        """
        # Trim whitespace
        corrected = alt_text.strip()

        # Check if image is marked as decorative
        is_decorative = False
        if corrected.upper() == "DECORATIVE":
            is_decorative = True
            corrected = ""  # Decorative images get empty alt-text
            return corrected, is_decorative

        # Remove excessive whitespace
        corrected = re.sub(r"\s+", " ", corrected)

        # Truncate if too long (max 350 chars for validation)
        if len(corrected) > self.MAX_LENGTH:
            logger.warning(
                f"Alt-text too long ({len(corrected)} chars), truncating to {self.MAX_LENGTH}"
            )
            # Truncate at word boundary near the limit
            truncate_point = self.MAX_LENGTH - 3  # Leave room for "..."
            # Find last space before truncate point
            last_space = corrected[:truncate_point].rfind(" ")
            if last_space > self.MAX_LENGTH * 0.8:  # Use word boundary if reasonable
                corrected = corrected[:last_space] + "..."
            else:
                corrected = corrected[:truncate_point] + "..."

        # Add period if missing (only if it doesn't end with punctuation)
        if corrected and not corrected[-1] in ".!?…":
            corrected += "."

        return corrected, is_decorative

    def _calculate_confidence_score(
        self,
        alt_text: str,
        is_decorative: bool,
        validation_passed: bool,
        warnings: list[str],
        has_context: bool,
    ) -> float:
        """
        Calculate confidence score based on quality factors.

        Confidence is based on:
        - Validation status (major factor)
        - Length appropriateness
        - Context availability
        - Number of warnings

        Args:
            alt_text: Generated alt-text.
            is_decorative: Whether image is decorative.
            validation_passed: Whether validation passed.
            warnings: List of validation warnings.
            has_context: Whether document context was available.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        # Start with base confidence
        confidence = 0.85

        # Decorative images get high confidence (simple decision)
        if is_decorative:
            return 0.95

        # Major deduction if validation failed
        if not validation_passed:
            confidence -= 0.25

        # Deduct for each warning
        confidence -= len(warnings) * 0.05

        # Check length quality
        length = len(alt_text)
        if self.PREFERRED_MIN <= length <= self.PREFERRED_MAX:
            confidence += 0.10  # Bonus for ideal length
        elif length < self.MIN_LENGTH:
            confidence -= 0.15  # Penalty for too short
        elif length > self.MAX_LENGTH:
            confidence -= 0.15  # Penalty for too long

        # Bonus for having context
        if has_context:
            confidence += 0.05

        # Ensure confidence stays within bounds
        return max(0.1, min(1.0, confidence))

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate estimated cost for token usage.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        input_cost = input_tokens * self.INPUT_COST_PER_TOKEN
        output_cost = output_tokens * self.OUTPUT_COST_PER_TOKEN
        return round(input_cost + output_cost, 6)
