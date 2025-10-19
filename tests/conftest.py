"""
Pytest configuration and shared fixtures.

This file is automatically loaded by pytest and provides
common fixtures and configuration for all tests.
"""

from pathlib import Path
from typing import Generator

import pytest

from ada_annotator.config import Settings


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """
    Provide a temporary directory for test files.

    Args:
        tmp_path: pytest's built-in temporary directory fixture

    Returns:
        Path: Temporary directory path
    """
    return tmp_path


@pytest.fixture
def test_settings() -> Settings:
    """
    Provide test configuration settings.

    Returns:
        Settings: Test settings with mock AI responses enabled
    """
    return Settings(
        environment="development",
        debug_mode=True,
        mock_ai_responses=True,
        ai_service_type="azure_openai",
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_api_key="test-key",
        azure_openai_deployment_name="test-deployment",
        temp_dir=Path("./test_temp"),
    )


@pytest.fixture
def sample_docx_path(temp_dir: Path) -> Path:
    """
    Provide path for a sample DOCX file.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to sample DOCX file location
    """
    return temp_dir / "sample.docx"


@pytest.fixture
def sample_image_path(temp_dir: Path) -> Path:
    """
    Provide path for a sample image file.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to sample image file location
    """
    return temp_dir / "sample.png"
