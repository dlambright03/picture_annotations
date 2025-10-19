"""
Configuration management for ADA Annotator.

Loads settings from environment variables using pydantic-settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    debug_mode: bool = True

    # AI Service Configuration
    ai_service_type: Literal["azure_openai", "openai"] = "azure_openai"

    # Azure OpenAI Settings
    azure_openai_endpoint: str = Field(default="", description="Azure OpenAI endpoint URL")
    azure_openai_api_key: str = Field(default="", description="Azure OpenAI API key")
    azure_openai_deployment_name: str = Field(
        default="", description="Azure OpenAI deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview", description="Azure OpenAI API version"
    )

    # OpenAI Settings
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")

    # AI Generation Settings
    ai_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    ai_max_tokens: int = Field(default=500, ge=1, le=4000)
    ai_timeout_seconds: int = Field(default=30, ge=1, le=300)

    # Alt-Text Settings
    max_alt_text_length: int = Field(default=250, ge=50, le=500)
    preferred_alt_text_length: int = Field(default=150, ge=50, le=250)

    # File Processing Settings
    max_upload_size_mb: int = Field(default=50, ge=1, le=500)
    max_images_per_document: int = Field(default=100, ge=1, le=1000)
    temp_dir: Path = Field(default=Path("./temp"))

    # Context Extraction Settings
    context_paragraphs_before: int = Field(default=2, ge=0, le=10)
    context_paragraphs_after: int = Field(default=2, ge=0, le=10)

    # CLI Settings
    dry_run: bool = False
    create_backup: bool = False
    log_file: Path = Field(default=Path("ada_annotator.log"))

    # Streamlit Settings
    streamlit_server_port: int = Field(default=8501, ge=1024, le=65535)
    streamlit_server_address: str = Field(default="localhost")

    # Testing & Development
    mock_ai_responses: bool = False
    mock_alt_text: str = "Sample alt text for testing purposes"

    @field_validator("temp_dir")
    @classmethod
    def validate_temp_dir(cls, v: Path) -> Path:
        """Ensure temp directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("preferred_alt_text_length")
    @classmethod
    def validate_preferred_length(cls, v: int, info) -> int:
        """Ensure preferred length is less than max length."""
        if "max_alt_text_length" in info.data and v > info.data["max_alt_text_length"]:
            raise ValueError("preferred_alt_text_length must be <= max_alt_text_length")
        return v

    def validate_ai_config(self) -> None:
        """Validate that required AI service credentials are present."""
        if self.ai_service_type == "azure_openai":
            if not self.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI service")
            if not self.azure_openai_api_key:
                raise ValueError("AZURE_OPENAI_API_KEY is required for Azure OpenAI service")
            if not self.azure_openai_deployment_name:
                raise ValueError(
                    "AZURE_OPENAI_DEPLOYMENT_NAME is required for Azure OpenAI service"
                )
        elif self.ai_service_type == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI service")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application configuration settings
    """
    settings = Settings()
    if not settings.mock_ai_responses:
        settings.validate_ai_config()
    return settings
