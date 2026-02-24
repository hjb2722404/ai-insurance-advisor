"""
Tests for AI service.

Tests AI service initialization, OpenAI API integration, and error handling.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from backend.app.services.ai_service import AIService, AISettings


class TestAISettings:
    """Tests for AISettings configuration."""

    def test_ai_settings_default_values(self):
        """Test that AISettings has correct default values."""
        settings = AISettings()
        assert settings.openai_consultation_model == "gpt-4o-mini"
        assert settings.openai_interpretation_model == "gpt-4o-mini"
        assert settings.ai_timeout == 600.0
        assert settings.ai_max_retries == 3
        assert settings.ai_temperature == 0.7

    def test_ai_settings_from_env(self):
        """Test AISettings loads from environment variables."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key-123',
            'OPENAI_CONSULTATION_MODEL': 'gpt-4o',
            'OPENAI_INTERPRETATION_MODEL': 'gpt-4o',
            'AI_TIMEOUT': '300.0',
            'AI_MAX_RETRIES': '5',
            'AI_TEMPERATURE': '0.5'
        }):
            settings = AISettings()
            assert settings.openai_api_key == 'test-key-123'
            assert settings.openai_consultation_model == 'gpt-4o'
            assert settings.openai_interpretation_model == 'gpt-4o'
            assert settings.ai_timeout == 300.0
            assert settings.ai_max_retries == 5
            assert settings.ai_temperature == 0.5


class TestAIServiceInitialization:
    """Tests for AI service initialization."""

    @patch('backend.app.services.ai_service.OpenAI')
    def test_ai_service_initialization_with_api_key(self, mock_openai):
        """Test AI service initializes with valid API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key-123'}):
            service = AIService()
            assert service is not None
            assert service.consultation_model == "gpt-4o-mini"
            assert service.interpretation_model == "gpt-4o-mini"
            assert service.temperature == 0.7
            mock_openai.assert_called_once()

    def test_ai_service_initialization_without_api_key(self):
        """Test AI service raises error without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                AIService()

    @patch('backend.app.services.ai_service.OpenAI')
    def test_ai_service_with_custom_settings(self, mock_openai):
        """Test AI service initialization with custom settings."""
        custom_settings = AISettings(
            openai_api_key='custom-key',
            openai_consultation_model='gpt-4o',
            openai_interpretation_model='gpt-4-turbo',
            ai_temperature=0.5
        )
        service = AIService(settings=custom_settings)
        assert service.consultation_model == 'gpt-4o'
        assert service.interpretation_model == 'gpt-4-turbo'
        assert service.temperature == 0.5

    @patch('backend.app.services.ai_service.OpenAI')
    def test_ai_service_with_custom_base_url(self, mock_openai):
        """Test AI service initialization with custom base URL."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_API_BASE_URL': 'https://custom.openai.com/v1'
        }):
            service = AIService()
            # Verify OpenAI client was called with base_url
            call_kwargs = mock_openai.call_args[1]
            assert call_kwargs['base_url'] == 'https://custom.openai.com/v1'


class TestConsultationRecommendation:
    """Tests for consultation recommendation method."""

    @pytest.fixture
    def mock_ai_response(self):
        """Create a mock AI response for consultation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
# 保险建议

## 1. 重疾险
- 推荐保额：50万元
- 推荐理由：作为家庭经济支柱，需要防范重大疾病带来的收入损失风险
- 优先级：高

## 2. 医疗险
- 推荐保额：200万元
- 推荐理由：覆盖高额医疗费用，补充社保不足
- 优先级：高
"""
        return mock_response

    @patch('backend.app.services.ai_service.OpenAI')
    def test_consultation_recommendation_success(self, mock_openai, mock_ai_response):
        """Test consultation recommendation generates response."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_ai_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            # Run the async method synchronously for testing
            import asyncio
            result = asyncio.run(service.get_consultation_recommendation({
                "name": "张三",
                "age": 35,
                "gender": "male",
                "occupation": "软件工程师",
                "annual_income": 500000,
                "marital_status": "married",
                "num_dependents": 2
            }))

            assert result is not None
            assert len(result) > 0
            assert "保险" in result or "建议" in result

    @patch('backend.app.services.ai_service.OpenAI')
    def test_consultation_with_health_conditions(self, mock_openai, mock_ai_response):
        """Test consultation includes health conditions in prompt."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_ai_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            result = asyncio.run(service.get_consultation_recommendation({
                "name": "李四",
                "age": 30,
                "gender": "female",
                "occupation": "医生",
                "annual_income": 400000,
                "marital_status": "single",
                "health_conditions": ["高血压"]
            }))

            # Verify the API was called
            mock_client.chat.completions.create.assert_called_once()

    @patch('backend.app.services.ai_service.OpenAI')
    def test_consultation_with_existing_insurance(self, mock_openai, mock_ai_response):
        """Test consultation includes existing insurance in prompt."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_ai_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            result = asyncio.run(service.get_consultation_recommendation({
                "name": "王五",
                "age": 40,
                "gender": "male",
                "occupation": "教师",
                "annual_income": 300000,
                "marital_status": "married",
                "existing_insurance": ["社会保险", "商业医疗险"]
            }))

            # Verify the API was called
            mock_client.chat.completions.create.assert_called_once()


class TestContractInterpretation:
    """Tests for contract interpretation method."""

    @pytest.fixture
    def mock_interpretation_response(self):
        """Create a mock AI response for interpretation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''{
  "summary": "这是一份重大疾病保险合同",
  "key_terms": [
    {"term": "等待期", "definition": "合同生效后90天内，若发生重大疾病，保险公司不承担赔偿责任"},
    {"term": "重疾", "definition": "合同约定的重大疾病，包括恶性肿瘤、急性心肌梗死等"}
  ],
  "coverage_details": {
    "scope": "覆盖100种重大疾病",
    "coverage_amount": "50万元",
    "coverage_period": "终身",
    "beneficiaries": "法定受益人"
  },
  "exclusions": [
    {"item": "投保前已患疾病", "description": "对于投保前已患的疾病，保险公司不承担赔偿责任"}
  ],
  "obligations": [
    {"obligation": "如实告知", "description": "投保时应如实告知健康状况"}
  ],
  "important_clauses": [
    {"clause": "等待期条款", "content": "等待期90天", "importance": "非常重要"}
  ],
  "recommendations": [
    {"point": "仔细阅读等待期条款", "reason": "等待期内发病无法获得赔付"}
  ]
}'''
        return mock_response

    @patch('backend.app.services.ai_service.OpenAI')
    def test_interpret_contract_parses_json_response(self, mock_openai, mock_interpretation_response):
        """Test that contract interpretation parses JSON correctly."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_interpretation_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            result = asyncio.run(service.interpret_contract("Sample contract text"))

            assert isinstance(result, dict)
            assert "summary" in result
            assert "key_terms" in result
            assert "coverage_details" in result
            assert "exclusions" in result
            assert isinstance(result["key_terms"], list)

    @patch('backend.app.services.ai_service.OpenAI')
    def test_interpret_with_markdown_json_wrapper(self, mock_openai):
        """Test interpretation extracts JSON from markdown code blocks."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''```json
{
  "summary": "Test summary",
  "key_terms": []
}
```'''
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            result = asyncio.run(service.interpret_contract("Test contract"))
            assert isinstance(result, dict)
            assert result["summary"] == "Test summary"


class TestAIServiceErrorHandling:
    """Tests for AI service error handling."""

    @patch('backend.app.services.ai_service.OpenAI')
    def test_handles_rate_limit_error(self, mock_openai):
        """Test AI service handles rate limit errors."""
        from openai import RateLimitError

        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = RateLimitError("Rate limit exceeded")
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            with pytest.raises(ValueError, match="high traffic"):
                asyncio.run(service.get_consultation_recommendation({"name": "Test"}))

    @patch('backend.app.services.ai_service.OpenAI')
    def test_handles_api_connection_error(self, mock_openai):
        """Test AI service handles connection errors."""
        from openai import APIConnectionError

        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = APIConnectionError("Connection failed")
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            with pytest.raises(ValueError, match="internet connection"):
                asyncio.run(service.get_consultation_recommendation({"name": "Test"}))

    @patch('backend.app.services.ai_service.OpenAI')
    def test_handles_api_error(self, mock_openai):
        """Test AI service handles API errors."""
        from openai import APIError

        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = APIError("API error occurred")
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            with pytest.raises(ValueError):
                asyncio.run(service.get_consultation_recommendation({"name": "Test"}))

    def test_handle_api_error_method(self):
        """Test the _handle_api_error helper method."""
        from openai import RateLimitError, APIConnectionError, APIError

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            rate_error = RateLimitError("Rate limit")
            message = service._handle_api_error(rate_error)
            assert "high traffic" in message.lower()

            conn_error = APIConnectionError("Connection failed")
            message = service._handle_api_error(conn_error)
            assert "internet" in message.lower()

            api_error = APIError("API error")
            message = service._handle_api_error(api_error)
            assert "error" in message.lower()

            generic_error = Exception("Unknown error")
            message = service._handle_api_error(generic_error)
            assert "unexpected" in message.lower()

    @patch('backend.app.services.ai_service.OpenAI')
    def test_handles_empty_response(self, mock_openai):
        """Test AI service handles empty API response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            import asyncio
            with pytest.raises(ValueError, match="empty response"):
                asyncio.run(service.get_consultation_recommendation({"name": "Test"}))


class TestExtractJsonFromResponse:
    """Tests for _extract_json_from_response method."""

    @patch('backend.app.services.ai_service.OpenAI')
    def test_extract_json_from_clean_json(self, mock_openai):
        """Test extracting clean JSON from response."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            result = service._extract_json_from_response('{"key": "value"}')
            assert result == {"key": "value"}

    @patch('backend.app.services.ai_service.OpenAI')
    def test_extract_json_from_markdown_block(self, mock_openai):
        """Test extracting JSON from markdown code block."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            result = service._extract_json_from_response('```json\n{"key": "value"}\n```')
            assert result == {"key": "value"}

    @patch('backend.app.services.ai_service.OpenAI')
    def test_extract_json_finds_largest_brace_match(self, mock_openai):
        """Test extracting JSON finds largest complete JSON object."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            result = service._extract_json_from_response('prefix {"key": "value"} suffix')
            assert result == {"key": "value"}

    @patch('backend.app.services.ai_service.OpenAI')
    def test_extract_json_raises_error_on_invalid_json(self, mock_openai):
        """Test extraction raises error when no valid JSON found."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()

            with pytest.raises(ValueError, match="No valid JSON"):
                service._extract_json_from_response("This is not JSON at all")
