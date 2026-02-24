"""
AI Service

Handles integration with OpenAI API for insurance consultation
and contract interpretation features.
"""

import os
from typing import Optional
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """Configuration settings for AI service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_api_base_url: Optional[str] = None
    openai_consultation_model: str = "gpt-4o-mini"
    openai_interpretation_model: str = "gpt-4o-mini"
    ai_timeout: float = 600.0  # 10 minutes for complex requests
    ai_max_retries: int = 3
    ai_temperature: float = 0.7


class AIService:
    """
    Service for interacting with OpenAI API.

    Provides methods for insurance consultation recommendations
    and contract interpretation analysis.
    """

    def __init__(self, settings: Optional[AISettings] = None) -> None:
        """
        Initialize the AI service with OpenAI client.

        Args:
            settings: Optional AISettings instance. If not provided,
                     loads from environment variables.

        Raises:
            ValueError: If OPENAI_API_KEY is not configured.
        """
        self._settings = settings or AISettings()

        if not self._settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable must be set. "
                "Create a .env file with your API key."
            )

        # Initialize OpenAI client with configuration
        client_kwargs = {
            "api_key": self._settings.openai_api_key,
            "timeout": self._settings.ai_timeout,
            "max_retries": self._settings.ai_max_retries,
        }

        if self._settings.openai_api_base_url:
            client_kwargs["base_url"] = self._settings.openai_api_base_url

        self._client = OpenAI(**client_kwargs)

    @property
    def consultation_model(self) -> str:
        """Get the model name for consultation requests."""
        return self._settings.openai_consultation_model

    @property
    def interpretation_model(self) -> str:
        """Get the model name for interpretation requests."""
        return self._settings.openai_interpretation_model

    @property
    def temperature(self) -> float:
        """Get the temperature setting for AI requests."""
        return self._settings.ai_temperature

    async def get_consultation_recommendation(self, user_info: dict) -> str:
        """
        Generate personalized insurance recommendations based on user information.

        This method will be implemented in subtask-2-2.

        Args:
            user_info: Dictionary containing user's personal and family information.

        Returns:
            AI-generated insurance recommendations as a string.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("get_consultation_recommendation will be implemented in subtask-2-2")

    async def interpret_contract(self, contract_text: str) -> dict:
        """
        Analyze insurance contract text and extract key information.

        This method will be implemented in subtask-2-3.

        Args:
            contract_text: Extracted text from insurance contract PDF.

        Returns:
            Dictionary containing contract analysis results.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("interpret_contract will be implemented in subtask-2-3")

    def _handle_api_error(self, error: Exception) -> str:
        """
        Convert OpenAI API errors to user-friendly error messages.

        Args:
            error: The exception raised by the OpenAI API.

        Returns:
            User-friendly error message.
        """
        if isinstance(error, RateLimitError):
            return "AI service is currently experiencing high traffic. Please try again later."
        elif isinstance(error, APIConnectionError):
            return "Unable to connect to AI service. Please check your internet connection."
        elif isinstance(error, APIError):
            return f"AI service error: {error.message}"
        else:
            return f"Unexpected error occurred: {str(error)}"
