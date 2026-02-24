"""
Consultation API Endpoint

Handles insurance plan consultation requests.
"""

import json
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from backend.app.models.requests import ConsultationRequest
from backend.app.models.responses import ConsultationResponse, InsuranceRecommendation
from backend.app.services.ai_service import AIService, AISettings


# Create FastAPI router for consultation endpoints
router = APIRouter(
    prefix="/api",
    tags=["consultation"],
)

# Initialize AI service (loaded from environment variables)
_ai_service = None


def get_ai_service() -> AIService:
    """
    Get or initialize the AI service singleton.

    Returns:
        AIService: The initialized AI service instance.

    Raises:
        HTTPException: If AI service initialization fails.
    """
    global _ai_service
    if _ai_service is None:
        try:
            _ai_service = AIService()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service initialization failed: {str(e)}"
            )
    return _ai_service


@router.post(
    "/consultation",
    response_model=ConsultationResponse,
    summary="Get insurance consultation",
    description="Submit personal information and receive AI-powered insurance recommendations",
)
async def get_consultation(request: ConsultationRequest) -> ConsultationResponse:
    """
    Generate personalized insurance recommendations based on user information.

    This endpoint accepts user and family information, validates it,
    and returns AI-generated insurance plan recommendations for:
    - Health/illness insurance (重疾险, 医疗险)
    - Accident insurance (意外险)
    - Pension/retirement insurance (养老保险)
    - Annuity insurance (年金保险)

    Args:
        request: ConsultationRequest containing user's personal and family information.

    Returns:
        ConsultationResponse: Structured insurance recommendations with reasoning.

    Raises:
        HTTPException: If AI service fails or returns invalid response.
    """
    try:
        # Get AI service
        ai_service = get_ai_service()

        # Convert request to dictionary for AI service
        user_info = request.model_dump()

        # Call AI service for recommendations
        ai_response = await ai_service.get_consultation_recommendation(user_info)

        # Parse AI response into structured recommendations
        recommendations = _parse_ai_recommendations(ai_response)

        # Extract reasoning from AI response
        reasoning = _extract_reasoning(ai_response)

        # Extract total estimated annual premium if present
        premium = _extract_premium(ai_response)

        # Extract next steps if present
        next_steps = _extract_next_steps(ai_response)

        return ConsultationResponse(
            success=True,
            recommendations=recommendations,
            reasoning=reasoning,
            total_estimated_annual_premium=premium,
            next_steps=next_steps,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle AI service errors
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}"
        )
    except ValidationError as e:
        # Handle request validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Request validation failed: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred: {str(e)}"
        )


def _parse_ai_recommendations(ai_response: str) -> List[InsuranceRecommendation]:
    """
    Parse AI response text into structured InsuranceRecommendation objects.

    Args:
        ai_response: Raw AI-generated recommendations text.

    Returns:
        List of InsuranceRecommendation objects.

    Note:
        This is a simplified parser that extracts structured data from
        the AI's natural language response. For production use, consider
        asking the AI to return structured JSON directly.
    """
    recommendations = []

    # If AI response contains JSON, try to parse it
    try:
        # Look for JSON blocks in the response
        import re
        json_pattern = r'\[\s*\{.*?\}\s*\]'
        matches = re.findall(json_pattern, ai_response, re.DOTALL)

        if matches:
            # Try to parse the largest JSON match
            largest_match = max(matches, key=len)
            data = json.loads(largest_match)

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        recommendations.append(InsuranceRecommendation(
                            insurance_type=item.get("insurance_type", "未知"),
                            recommended_coverage=item.get("recommended_coverage", "待确定"),
                            reason=item.get("reason", "根据AI分析建议"),
                            priority=item.get("priority", "medium"),
                        ))
                return recommendations
    except (json.JSONDecodeError, ValueError):
        # Fall through to text-based parsing
        pass

    # Text-based fallback parsing
    # Look for common patterns in Chinese insurance recommendations
    lines = ai_response.split('\n')
    current_recommendation = {}

    for line in lines:
        line = line.strip()

        # Detect insurance type (e.g., "1. 重疾险" or "重疾险：")
        if any(keyword in line for keyword in ["重疾险", "医疗险", "意外险", "养老保险", "年金保险"]):
            # Save previous recommendation if exists
            if current_recommendation:
                recommendations.append(_build_recommendation(current_recommendation))
                current_recommendation = {}

            # Extract insurance type
            for keyword in ["重疾险", "医疗险", "意外险", "养老保险", "年金保险"]:
                if keyword in line:
                    current_recommendation["insurance_type"] = keyword
                    break

        # Detect coverage (e.g., "保额：50万元")
        elif "保额" in line or "coverage" in line.lower():
            current_recommendation["recommended_coverage"] = line.split("：")[-1].split(":")[-1].strip()

        # Detect priority
        elif "优先级" in line or "priority" in line.lower():
            priority = line.split("：")[-1].split(":")[-1].strip().lower()
            if "高" in priority or "high" in priority:
                current_recommendation["priority"] = "high"
            elif "低" in priority or "low" in priority:
                current_recommendation["priority"] = "low"
            else:
                current_recommendation["priority"] = "medium"

        # Detect reason (e.g., "理由：..." or "推荐理由：...")
        elif "理由" in line or "reason" in line.lower() or "原因" in line:
            current_recommendation["reason"] = line.split("：")[-1].split(":")[-1].strip()

    # Don't forget the last recommendation
    if current_recommendation:
        recommendations.append(_build_recommendation(current_recommendation))

    # If parsing failed, return a generic recommendation
    if not recommendations:
        recommendations.append(InsuranceRecommendation(
            insurance_type="综合保险建议",
            recommended_coverage="根据您的具体情况定制",
            reason="AI分析完成，建议详细阅读完整回复",
            priority="medium",
        ))

    return recommendations


def _build_recommendation(data: dict) -> InsuranceRecommendation:
    """
    Build an InsuranceRecommendation from a dictionary.

    Args:
        data: Dictionary with recommendation fields.

    Returns:
        InsuranceRecommendation object.
    """
    return InsuranceRecommendation(
        insurance_type=data.get("insurance_type", "未知"),
        recommended_coverage=data.get("recommended_coverage", "待确定"),
        reason=data.get("reason", "根据AI分析建议"),
        priority=data.get("priority", "medium"),
    )


def _extract_reasoning(ai_response: str) -> str:
    """
    Extract the overall reasoning from AI response.

    Args:
        ai_response: Raw AI-generated recommendations text.

    Returns:
        The reasoning text, or a summary if too long.
    """
    # For now, return the first 500 characters as reasoning
    # In production, you might want to parse specific sections
    reasoning = ai_response[:500].strip()

    if len(ai_response) > 500:
        reasoning += "...（详见完整回复）"

    return reasoning


def _extract_premium(ai_response: str) -> str:
    """
    Extract estimated annual premium from AI response.

    Args:
        ai_response: Raw AI-generated recommendations text.

    Returns:
        Premium string or None if not found.
    """
    import re

    # Look for premium patterns like "保费：8,000元" or "预计保费：8000-12000元"
    premium_patterns = [
        r'保费[：:]\s*([\d,，\s\-~到至]+元)',
        r'预计保费[：:]\s*([\d,，\s\-~到至]+元)',
        r'总保费[：:]\s*([\d,，\s\-~到至]+元)',
    ]

    for pattern in premium_patterns:
        match = re.search(pattern, ai_response)
        if match:
            return match.group(1).strip()

    return None


def _extract_next_steps(ai_response: str) -> List[str]:
    """
    Extract next steps from AI response.

    Args:
        ai_response: Raw AI-generated recommendations text.

    Returns:
        List of next step strings.
    """
    next_steps = []

    # Look for "下一步" or "建议" section
    lines = ai_response.split('\n')
    capture_next = False

    for line in lines:
        line = line.strip()

        # Detect start of next steps section
        if any(keyword in line for keyword in ["下一步", "建议行动", "后续步骤"]):
            capture_next = True
            continue

        # Stop capturing if we hit a new major section
        if capture_next and line.startswith('#'):
            break

        # Capture list items
        if capture_next and (line.startswith('-') or line.startswith('*') or line[0].isdigit() + '.' == line[:2]):
            step = line.lstrip('-*').lstrip('0123456789.')
            step = step.strip('、. ')
            if step:
                next_steps.append(step)

    return next_steps
