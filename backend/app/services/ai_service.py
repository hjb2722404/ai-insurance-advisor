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

        Uses OpenAI API to analyze user's personal and family circumstances
        and provide tailored insurance recommendations for health/illness,
        accident, pension/retirement, and annuity insurance types.

        Args:
            user_info: Dictionary containing user's personal and family information.
                      Expected keys: name, age, gender, occupation, annual_income,
                      marital_status, num_dependents, health_conditions,
                      existing_insurance, additional_notes.

        Returns:
            AI-generated insurance recommendations as a formatted string.

        Raises:
            ValueError: If API call fails or returns invalid response.
        """
        # System prompt defining AI behavior as professional insurance advisor
        system_prompt = """你是一位专业且值得信赖的保险顾问，专门为个人客户提供保险规划建议。

你的职责：
1. 根据客户提供的个人信息（年龄、收入、家庭状况、健康状况等），分析其保险需求
2. 推荐适合的保险类型和保额，重点关注以下四大类个人保险：
   - 健康保险/疾病保险（重疾险、医疗险）
   - 意外保险
   - 养老保险/退休保险
   - 年金保险
3. 解释推荐理由，说明为什么这些保险适合该客户
4. 考虑客户的现有保险，避免重复推荐
5. 考虑客户的健康状况，推荐可承保的保险产品
6. 提供优先级排序，帮助客户了解哪些保险最急需配置
7. 给出估算的保费范围（基于行业经验）
8. 建议下一步行动

回答格式要求：
- 使用清晰的标题和分段
- 每个保险建议包含：保险类型、推荐保额、推荐理由、优先级
- 最后提供整体建议总结和下一步行动建议
- 语言应专业但不失亲和力，便于普通客户理解
- 如果信息不足，请在回复中指明需要补充的信息

重要提醒：
- 不推荐超出项目范围的保险类型（如车险、教育险）
- 建议应基于客户的实际经济能力，避免过度保险
- 强调如实告知健康状况的重要性
- 提醒客户仔细阅读保险条款，特别是等待期和免责条款"""

        # Format user information for the prompt
        user_prompt = self._format_user_info_for_prompt(user_info)

        try:
            # Call OpenAI API
            response = self._client.chat.completions.create(
                model=self.consultation_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=2500,
            )

            # Extract and return the AI-generated recommendations
            recommendations = response.choices[0].message.content

            if not recommendations:
                raise ValueError("AI service returned empty response")

            return recommendations

        except (APIError, APIConnectionError, RateLimitError) as e:
            error_message = self._handle_api_error(e)
            raise ValueError(error_message) from e
        except Exception as e:
            error_message = self._handle_api_error(e)
            raise ValueError(error_message) from e

    def _format_user_info_for_prompt(self, user_info: dict) -> str:
        """
        Format user information into a structured prompt for AI.

        Args:
            user_info: Dictionary containing user's personal and family information.

        Returns:
            Formatted string with user information.
        """
        prompt_parts = [
            "请根据以下客户信息，为其提供个性化的保险规划建议：\n",
        ]

        # Basic information
        prompt_parts.append("【基本信息】")
        prompt_parts.append(f"姓名：{user_info.get('name', '未知')}")
        prompt_parts.append(f"年龄：{user_info.get('age', '未知')}岁")
        prompt_parts.append(f"性别：{user_info.get('gender', '未知')}")
        prompt_parts.append(f"职业：{user_info.get('occupation', '未知')}")
        prompt_parts.append(f"年收入：{user_info.get('annual_income', 0):,.0f}元")

        # Family situation
        prompt_parts.append("\n【家庭状况】")
        prompt_parts.append(f"婚姻状况：{user_info.get('marital_status', '未知')}")
        prompt_parts.append(f"受抚养人数：{user_info.get('num_dependents', 0)}人")

        # Health conditions
        health_conditions = user_info.get('health_conditions')
        if health_conditions:
            prompt_parts.append("\n【健康状况】")
            prompt_parts.append("已告知健康问题：")
            for condition in health_conditions:
                prompt_parts.append(f"  - {condition}")
        else:
            prompt_parts.append("\n【健康状况】")
            prompt_parts.append("未告知特殊健康问题")

        # Existing insurance
        existing_insurance = user_info.get('existing_insurance')
        if existing_insurance:
            prompt_parts.append("\n【已有保险】")
            prompt_parts.append("已配置保险：")
            for insurance in existing_insurance:
                prompt_parts.append(f"  - {insurance}")
        else:
            prompt_parts.append("\n【已有保险】")
            prompt_parts.append("未配置商业保险")

        # Additional notes
        additional_notes = user_info.get('additional_notes')
        if additional_notes:
            prompt_parts.append(f"\n【其他说明】")
            prompt_parts.append(additional_notes)

        prompt_parts.append("\n\n请根据以上信息，提供详细的保险规划建议。")

        return "\n".join(prompt_parts)

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
