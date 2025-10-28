"""
Semantic Kernel integration for AI-powered alt-text generation.

Provides Azure OpenAI integration using Microsoft Semantic Kernel.
"""


from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (  # noqa: E501
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.image_content import ImageContent

from ada_annotator.config import Settings
from ada_annotator.exceptions import APIError
from ada_annotator.models import ImageMetadata
from ada_annotator.utils.image_utils import convert_image_to_base64
from ada_annotator.utils.logging import get_logger

logger = get_logger(__name__)


# System prompt for alt-text generation
ALT_TEXT_SYSTEM_PROMPT = """You are an accessibility expert creating alt-text for educational documents.

Your task is to analyze images and generate concise, descriptive alternative text that meets ADA compliance standards.

Guidelines:
- Be concise but descriptive (100-150 characters preferred, max 250)
- Describe the essential content and purpose of the image
- Avoid phrases like "image of", "picture of", or "graphic showing"
- For charts/graphs: Include key data points and trends
- For diagrams: Describe structure and relationships
- For screenshots: Describe UI elements and their purpose
- Use objective, factual language
- Match the technical level of the surrounding content
- Start with a capital letter and end with a period

Remember: Your description helps visually impaired users understand the image's content and purpose."""


class SemanticKernelService:
    """
    AI service for generating alt-text using Semantic Kernel.

    Integrates with Azure OpenAI to provide vision-based image analysis
    and alt-text generation.

    Attributes:
        settings: Application settings
        kernel: Semantic Kernel instance
        service_id: AI service identifier
    """

    def __init__(self, settings: Settings):
        """
        Initialize Semantic Kernel service with Azure OpenAI.

        Args:
            settings: Application configuration settings

        Raises:
            ValueError: If Azure OpenAI credentials are missing
        """
        self.settings = settings
        self.service_id = "azure_chat_completion"

        # Validate configuration
        settings.validate_ai_config()

        # Initialize kernel
        self.kernel = Kernel()

        # Add Azure OpenAI chat completion service
        self.kernel.add_service(
            AzureChatCompletion(
                service_id=self.service_id,
                deployment_name=settings.azure_openai_deployment_name,
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
        )

        logger.info(
            f"Initialized Semantic Kernel with Azure OpenAI "
            f"(deployment: {settings.azure_openai_deployment_name})"
        )

    def _get_execution_settings(self) -> AzureChatPromptExecutionSettings:
        """
        Create execution settings for chat completion.

        Returns:
            Configured execution settings
        """
        return AzureChatPromptExecutionSettings(
            service_id=self.service_id,
            temperature=self.settings.ai_temperature,
            max_tokens=self.settings.ai_max_tokens,
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )

    def _build_chat_history(
        self, context: str, image_base64: str
    ) -> ChatHistory:
        """
        Build multi-modal chat history with system prompt, context, and image.

        Args:
            context: Textual context about the image
            image_base64: Base64 encoded image data

        Returns:
            ChatHistory with system message and user message containing
            text and image
        """
        history = ChatHistory()

        # Add system message with alt-text guidelines
        history.add_system_message(ALT_TEXT_SYSTEM_PROMPT)

        # Add user message with context text
        context_message = (
            f"Context from document:\n{context}\n\n"
            f"Please analyze the provided image and generate appropriate "
            f"alt-text based on this context."
        )
        history.add_user_message(context_message)

        # Add user message with image content
        # Note: Semantic Kernel expects images as data URIs
        data_uri = f"data:image/png;base64,{image_base64}"

        image_message = ChatMessageContent(
            role="user",
            items=[ImageContent(uri=data_uri)],
        )
        history.add_message(image_message)

        return history

    def _prepare_image(self, image_path: str) -> str:
        """
        Convert image file to base64 for API transmission.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string

        Raises:
            APIError: If image cannot be read or converted
        """
        try:
            return convert_image_to_base64(image_path, include_prefix=False)
        except Exception as e:
            logger.error(f"Failed to prepare image {image_path}: {e}")
            raise APIError(f"Image preparation failed: {e}") from e

    async def generate_alt_text(
        self, image_metadata: ImageMetadata, context: str
    ) -> str:
        """
        Generate alt-text for an image using Azure OpenAI vision model.

        Args:
            image_metadata: Metadata about the image
            context: Textual context about the image

        Returns:
            Generated alt-text description

        Raises:
            APIError: If generation fails or times out

        Example:
            >>> service = SemanticKernelService(settings)
            >>> alt_text = await service.generate_alt_text(
            ...     image_metadata=img_meta,
            ...     context="Biology textbook diagram"
            ... )
            >>> print(alt_text)
            "Diagram of a plant cell showing nucleus, chloroplasts, and
            cell wall."
        """
        try:
            # Convert image to base64
            image_base64 = self._prepare_image(image_metadata.filename)

            # Build chat history with context and image
            chat_history = self._build_chat_history(context, image_base64)

            # Get execution settings
            execution_settings = self._get_execution_settings()

            logger.info(
                f"Generating alt-text for image {image_metadata.image_id}"
            )

            # Call Azure OpenAI
            response = await self.kernel.get_chat_message_content_async(
                chat_history=chat_history,
                settings=execution_settings,
            )

            # Extract text from response
            alt_text = str(response.content).strip()

            logger.info(
                f"Generated alt-text for {image_metadata.image_id}: "
                f"{alt_text[:50]}..."
            )

            return alt_text

        except TimeoutError as e:
            logger.error(f"Timeout generating alt-text: {e}")
            raise APIError(
                "AI service timeout - request took too long", status_code=504
            ) from e
        except Exception as e:
            logger.error(f"Failed to generate alt-text: {e}")
            # Check if it's a rate limit or service error
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                raise APIError("Rate limit exceeded", status_code=429) from e
            elif "503" in error_msg or "unavailable" in error_msg:
                raise APIError("Service unavailable", status_code=503) from e
            else:
                raise APIError(f"Alt-text generation failed: {e}") from e

    async def check_availability(self) -> bool:
        """
        Check if AI service is available and accessible.

        Returns:
            True if service is available, False otherwise

        Example:
            >>> service = SemanticKernelService(settings)
            >>> if await service.check_availability():
            ...     print("Service ready")
            ... else:
            ...     print("Service unavailable")
        """
        try:
            # Simple test call
            test_history = ChatHistory()
            test_history.add_user_message("test")

            settings = self._get_execution_settings()

            await self.kernel.get_chat_message_content_async(
                chat_history=test_history,
                settings=settings,
            )

            logger.info("AI service availability check: SUCCESS")
            return True

        except Exception as e:
            logger.error(f"AI service availability check failed: {e}")
            return False
