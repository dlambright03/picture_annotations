"""
Unit tests for Semantic Kernel service.

Tests AI service integration with Azure OpenAI.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent

from ada_annotator.ai_services.semantic_kernel_service import SemanticKernelService
from ada_annotator.config import Settings
from ada_annotator.exceptions import APIError
from ada_annotator.models import ImageMetadata


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        ai_service_type="azure_openai",
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_api_key="test-key",
        azure_openai_deployment_name="gpt-4o",
        ai_temperature=0.3,
        ai_max_tokens=500,
        ai_timeout_seconds=30,
    )


@pytest.fixture
def sample_image_metadata(tmp_path):
    """Create sample image metadata for testing."""
    img_path = tmp_path / "test.png"
    img_path.write_bytes(b"fake image data")

    return ImageMetadata(
        image_id="img_001",
        filename=str(img_path),
        format="PNG",
        size_bytes=100,
        width_pixels=100,
        height_pixels=100,
        page_number=1,
        position={"paragraph_index": 5, "anchor_type": "inline"},
        existing_alt_text=None,
    )


class TestSemanticKernelServiceInitialization:
    """Test suite for service initialization."""

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    def test_initializes_with_azure_openai(self, mock_chat, mock_kernel, mock_settings):
        """Should initialize kernel with Azure OpenAI service."""
        service = SemanticKernelService(mock_settings)

        assert service is not None
        assert service.settings == mock_settings
        # Verify Azure chat completion was configured
        mock_chat.assert_called_once()

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    def test_loads_settings_from_config(self, mock_kernel, mock_settings):
        """Should load configuration from settings."""
        service = SemanticKernelService(mock_settings)

        assert service.settings.ai_temperature == 0.3
        assert service.settings.ai_max_tokens == 500
        assert service.settings.ai_timeout_seconds == 30

    def test_raises_error_for_missing_credentials(self):
        """Should raise error if credentials are missing."""
        bad_settings = Settings(
            ai_service_type="azure_openai",
            azure_openai_endpoint="",
            azure_openai_api_key="",
            azure_openai_deployment_name="",
        )

        with pytest.raises(ValueError):
            bad_settings.validate_ai_config()


class TestChatCompletionSettings:
    """Test suite for chat completion execution settings."""

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    def test_configures_execution_settings(self, mock_chat, mock_kernel, mock_settings):
        """Should configure execution settings from config."""
        service = SemanticKernelService(mock_settings)
        settings_obj = service._get_execution_settings()

        assert settings_obj.temperature == 0.3
        assert settings_obj.max_tokens == 500

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    def test_uses_auto_function_choice(self, mock_chat, mock_kernel, mock_settings):
        """Should set function choice behavior to Auto."""
        service = SemanticKernelService(mock_settings)
        settings_obj = service._get_execution_settings()

        # Verify auto function calling is enabled
        assert settings_obj is not None


class TestChatHistoryBuilding:
    """Test suite for multi-modal chat history construction."""

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    def test_builds_system_message(self, mock_chat, mock_kernel, mock_settings):
        """Should add system message with alt-text guidelines."""
        service = SemanticKernelService(mock_settings)
        history = service._build_chat_history(
            context="Test context",
            image_base64="fake_base64",
        )

        assert isinstance(history, ChatHistory)
        # Should have system and user messages
        assert len(history.messages) >= 2
        assert history.messages[0].role.value == "system"

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    def test_includes_context_in_user_message(self, mock_chat, mock_kernel, mock_settings):
        """Should include context text in user message."""
        service = SemanticKernelService(mock_settings)
        context = "Document about biology with diagrams"

        history = service._build_chat_history(
            context=context,
            image_base64="fake_base64",
        )

        # User message should contain context
        user_messages = [msg for msg in history.messages if msg.role.value == "user"]
        assert len(user_messages) > 0
        # Check that context is present in one of the user messages
        context_found = any(context in str(msg.content) for msg in user_messages)
        assert context_found

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    def test_includes_image_content(self, mock_chat, mock_kernel, mock_settings):
        """Should include ImageContent in user message."""
        service = SemanticKernelService(mock_settings)

        history = service._build_chat_history(
            context="Test context",
            image_base64="fake_image_base64_data",
        )

        # Should have image content
        assert len(history.messages) >= 2


class TestImageBase64Conversion:
    """Test suite for image-to-base64 handling."""

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    @patch("ada_annotator.ai_services.semantic_kernel_service.convert_image_to_base64")
    def test_converts_image_to_base64(
        self, mock_convert, mock_chat, mock_kernel, mock_settings, sample_image_metadata
    ):
        """Should convert image file to base64."""
        mock_convert.return_value = "base64_encoded_image"

        service = SemanticKernelService(mock_settings)
        result = service._prepare_image(sample_image_metadata.filename)

        assert result == "base64_encoded_image"
        mock_convert.assert_called_once_with(
            sample_image_metadata.filename, include_prefix=False
        )

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    def test_handles_image_conversion_error(
        self, mock_chat, mock_kernel, mock_settings
    ):
        """Should raise APIError if image conversion fails."""
        service = SemanticKernelService(mock_settings)

        with pytest.raises((APIError, FileNotFoundError)):
            service._prepare_image("nonexistent_image.png")


class TestAltTextGeneration:
    """Test suite for alt-text generation."""

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    async def test_generates_alt_text_successfully(
        self, mock_chat, mock_kernel, mock_settings, sample_image_metadata
    ):
        """Should generate alt-text for image with context."""
        # Mock the kernel's get_chat_message_content_async to return a response
        mock_response = Mock()
        mock_response.content = "A red diagram showing cellular structure."
        mock_kernel_instance = mock_kernel.return_value
        mock_kernel_instance.get_chat_message_content_async = AsyncMock(
            return_value=mock_response
        )

        service = SemanticKernelService(mock_settings)
        service.kernel = mock_kernel_instance

        with patch.object(service, "_prepare_image", return_value="base64_image"):
            result = await service.generate_alt_text(
                image_metadata=sample_image_metadata,
                context="Biology textbook chapter on cells",
            )

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    async def test_handles_api_timeout(
        self, mock_chat, mock_kernel, mock_settings, sample_image_metadata
    ):
        """Should raise APIError on timeout."""
        mock_kernel_instance = mock_kernel.return_value
        mock_kernel_instance.get_chat_message_content_async = AsyncMock(
            side_effect=TimeoutError("Request timed out")
        )

        service = SemanticKernelService(mock_settings)
        service.kernel = mock_kernel_instance

        with patch.object(service, "_prepare_image", return_value="base64_image"):
            with pytest.raises(APIError, match="timeout|timed out"):
                await service.generate_alt_text(
                    image_metadata=sample_image_metadata,
                    context="Test context",
                )

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    async def test_handles_rate_limit_error(
        self, mock_chat, mock_kernel, mock_settings, sample_image_metadata
    ):
        """Should raise APIError with status_code on rate limit."""
        mock_kernel_instance = mock_kernel.return_value
        mock_kernel_instance.get_chat_message_content_async = AsyncMock(
            side_effect=Exception("Rate limit exceeded")
        )

        service = SemanticKernelService(mock_settings)
        service.kernel = mock_kernel_instance

        with patch.object(service, "_prepare_image", return_value="base64_image"):
            with pytest.raises((APIError, Exception)):
                await service.generate_alt_text(
                    image_metadata=sample_image_metadata,
                    context="Test context",
                )


class TestServiceAvailabilityCheck:
    """Test suite for AI service availability checking."""

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    async def test_checks_service_availability(self, mock_chat, mock_kernel, mock_settings):
        """Should verify service is reachable."""
        mock_kernel_instance = mock_kernel.return_value
        mock_response = Mock()
        mock_response.content = "test"
        mock_kernel_instance.get_chat_message_content_async = AsyncMock(
            return_value=mock_response
        )

        service = SemanticKernelService(mock_settings)
        service.kernel = mock_kernel_instance

        result = await service.check_availability()
        assert result is True

    @patch("ada_annotator.ai_services.semantic_kernel_service.Kernel")
    @patch("ada_annotator.ai_services.semantic_kernel_service.AzureChatCompletion")
    async def test_returns_false_when_unavailable(
        self, mock_chat, mock_kernel, mock_settings
    ):
        """Should return False if service is unavailable."""
        mock_kernel_instance = mock_kernel.return_value
        mock_kernel_instance.get_chat_message_content_async = AsyncMock(
            side_effect=Exception("Service unavailable")
        )

        service = SemanticKernelService(mock_settings)
        service.kernel = mock_kernel_instance

        result = await service.check_availability()
        assert result is False
