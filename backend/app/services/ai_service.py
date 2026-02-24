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

        Uses OpenAI API to analyze contract content and provide structured
        interpretation of key terms, coverage details, exclusions, and
        important clauses.

        Args:
            contract_text: Extracted text from insurance contract PDF.

        Returns:
            Dictionary containing contract analysis results with keys:
            - summary: Brief overview of the contract
            - key_terms: List of important terms and definitions
            - coverage_details: Coverage scope and limits
            - exclusions: List of exclusions and exceptions
            - obligations: Policyholder obligations
            - important_clauses: Notable clauses requiring attention
            - recommendations: Important points to consider

        Raises:
            ValueError: If API call fails or returns invalid response.
        """
        # System prompt for contract analysis
        system_prompt = """你是一位专业的保险合同分析专家，擅长解读各类保险合同的条款和内容。

你的职责：
1. 仔细分析用户提供的保险合同文本，提取关键信息
2. 用清晰易懂的语言解释专业术语和条款
3. 识别合同中的重要条款、保障范围、免责条款等
4. 指出合同中需要注意的重点和潜在风险点
5. 为用户提供客观、专业的合同解读

分析结构要求：
请按以下结构返回分析结果（使用JSON格式）：

{
  "summary": "合同简要概述，包括保险类型、投保人、被保险人、保险金额等基本信息",
  "key_terms": [
    {"term": "术语名称", "definition": "术语解释"}
  ],
  "coverage_details": {
    "scope": "保障范围描述",
    "coverage_amount": "保险金额/保额",
    "coverage_period": "保险期间",
    "beneficiaries": "受益人信息"
  },
  "exclusions": [
    {"item": "免责/除外责任项目", "description": "详细说明"}
  ],
  "obligations": [
    {"obligation": "义务项", "description": "具体说明"}
  ],
  "important_clauses": [
    {"clause": "条款名称", "content": "条款内容摘要", "importance": "重要性说明"}
  ],
  "recommendations": [
    {"point": "注意事项或建议", "reason": "原因说明"}
  ]
}

注意事项：
- 如果合同文本不完整或难以识别某些内容，请在相应部分注明
- 保持分析客观中立，不偏向保险公司或投保人任何一方
- 对于免责条款要特别关注并明确指出
- 如果发现合同中存在不合理或异常条款，请在recommendations中重点说明
- 确保返回的是有效的JSON格式"""

        # User prompt with contract text
        user_prompt = f"""请分析以下保险合同文本，并提供详细的解读：

【保险合同文本】
{contract_text}

请按照指定的JSON格式返回分析结果。"""

        try:
            # Call OpenAI API
            response = self._client.chat.completions.create(
                model=self.interpretation_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent structured output
                max_tokens=4000,
            )

            # Extract the AI-generated analysis
            analysis = response.choices[0].message.content

            if not analysis:
                raise ValueError("AI service returned empty response")

            # Parse the JSON response
            import json

            # Try to extract JSON from the response (in case there's extra text)
            analysis_json = self._extract_json_from_response(analysis)

            return analysis_json

        except (APIError, APIConnectionError, RateLimitError) as e:
            error_message = self._handle_api_error(e)
            raise ValueError(error_message) from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}") from e
        except Exception as e:
            error_message = self._handle_api_error(e)
            raise ValueError(error_message) from e

    def _extract_json_from_response(self, response: str) -> dict:
        """
        Extract JSON from AI response, handling potential extra text.

        Args:
            response: The raw response string from the AI.

        Returns:
            Parsed dictionary from JSON content.

        Raises:
            ValueError: If no valid JSON is found in the response.
        """
        import json
        import re

        # First, try to parse the entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # If that fails, try to extract JSON using regex
        # Look for content between ```json and ``` markers
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass

        # Try to find content between { and } (assuming JSON object)
        brace_pattern = r'\{.*\}'
        matches = re.findall(brace_pattern, response, re.DOTALL)
        if matches:
            try:
                # Get the largest match (most likely to be complete JSON)
                largest_match = max(matches, key=len)
                return json.loads(largest_match)
            except json.JSONDecodeError:
                pass

        # If all attempts fail, raise an error
        raise ValueError("No valid JSON found in AI response")

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
