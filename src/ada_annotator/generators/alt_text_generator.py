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
    MAX_LENGTH = 250
    PREFERRED_MIN = 50
    PREFERRED_MAX = 200

    # Forbidden phrases in alt-text
    FORBIDDEN_PHRASES = [
        "image of",
        "picture of",
        "graphic showing",
        "photo of",
        "screenshot of",
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
                local_context="",
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

        # Auto-correct alt-text
        alt_text = self._auto_correct_alt_text(raw_alt_text)

        # Validate alt-text
        validation_passed, warnings = self._validate_alt_text(alt_text)

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
            confidence_score=0.85,  # Default confidence
            validation_passed=validation_passed,
            validation_warnings=warnings,
            tokens_used=total_tokens,
            processing_time_seconds=round(processing_time, 3),
        )

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

        # Check capitalization
        if alt_text and not alt_text[0].isupper():
            warnings.append("Alt-text should start with uppercase letter")

        # Check for ending punctuation (period expected)
        if not alt_text.endswith("."):
            warnings.append("Alt-text should end with a period")

        return passed, warnings

    def _auto_correct_alt_text(self, alt_text: str) -> str:
        """
        Apply automatic corrections to alt-text.

        Args:
            alt_text: Raw alt-text from AI.

        Returns:
            Corrected alt-text.
        """
        # Trim whitespace
        corrected = alt_text.strip()

        # Remove excessive whitespace
        corrected = re.sub(r"\s+", " ", corrected)

        # Add period if missing
        if corrected and not corrected.endswith("."):
            corrected += "."

        return corrected

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
