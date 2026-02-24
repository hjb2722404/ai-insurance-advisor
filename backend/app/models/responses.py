"""
Response Models

Pydantic models for structuring API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class InsuranceRecommendation(BaseModel):
    """
    Single insurance recommendation.
    """
    insurance_type: str = Field(
        ...,
        description="Type of insurance (e.g., '健康保险', '意外保险', '养老保险', '年金保险')"
    )
    recommended_coverage: str = Field(
        ...,
        description="Recommended coverage amount or limit"
    )
    reason: str = Field(
        ...,
        description="Explanation for why this insurance is recommended"
    )
    priority: str = Field(
        default="medium",
        description="Priority level: 'high', 'medium', or 'low'"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "insurance_type": "重疾险",
                "recommended_coverage": "50万元保额",
                "reason": "考虑到您有家庭依赖，建议配置重疾险以应对重大疾病风险",
                "priority": "high"
            }
        }
    )


class ConsultationResponse(BaseModel):
    """
    Response model for insurance consultation.

    Contains AI-generated personalized insurance recommendations.
    """
    success: bool = Field(
        default=True,
        description="Indicates if the consultation was successful"
    )
    recommendations: List[InsuranceRecommendation] = Field(
        ...,
        description="List of recommended insurance plans"
    )
    reasoning: str = Field(
        ...,
        description="Overall reasoning and explanation for the recommendations"
    )
    total_estimated_annual_premium: Optional[str] = Field(
        default=None,
        description="Estimated total annual premium for all recommended plans"
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Suggested next steps for the user"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "recommendations": [
                    {
                        "insurance_type": "重疾险",
                        "recommended_coverage": "50万元保额",
                        "reason": "考虑到您有家庭依赖，建议配置重疾险以应对重大疾病风险",
                        "priority": "high"
                    },
                    {
                        "insurance_type": "意外险",
                        "recommended_coverage": "100万元保额",
                        "reason": "作为家庭经济支柱，意外险可提供额外保障",
                        "priority": "high"
                    }
                ],
                "reasoning": "根据您35岁、已婚、有两个受抚养人的情况，我们建议优先配置保障型保险...",
                "total_estimated_annual_premium": "约8,000-12,000元",
                "next_steps": [
                    "联系保险顾问获取详细方案",
                    "比较不同保险公司的产品",
                    "注意等待期和免责条款"
                ]
            }
        }
    )


class ContractTerm(BaseModel):
    """
    Key term from insurance contract.
    """
    term: str = Field(..., description="The term or clause name")
    explanation: str = Field(..., description="Plain-language explanation of the term")
    importance: str = Field(
        default="medium",
        description="Importance level: 'critical', 'high', 'medium', or 'low'"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "term": "等待期",
                "explanation": "投保后90天内发生的疾病，保险公司不承担赔偿责任。这是为了防止带病投保。",
                "importance": "critical"
            }
        }
    )


class PayoutCondition(BaseModel):
    """
    Condition for insurance payout.
    """
    condition: str = Field(..., description="The payout condition")
    description: str = Field(..., description="Detailed description of when this applies")
    required_documents: Optional[List[str]] = Field(
        default=None,
        description="Documents required to claim this payout"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "condition": "确诊合同约定的重大疾病",
                "description": "被保险人经医院确诊初次发生合同约定的重大疾病",
                "required_documents": ["诊断证明书", "病历资料", "身份证明"]
            }
        }
    )


class PayoutDetails(BaseModel):
    """
    Detailed payout information.
    """
    payout_method: str = Field(..., description="How the payout is calculated/delivered")
    payout_amount: str = Field(..., description="Payout amount or calculation method")
    payout_timeline: str = Field(..., description="Expected timeline for payout")
    limitations: Optional[List[str]] = Field(
        default=None,
        description="Any limitations or exclusions on payouts"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payout_method": "一次性给付",
                "payout_amount": "基本保额50万元",
                "payout_timeline": "审核通过后10个工作日内",
                "limitations": ["等待期内不赔付", "免责条款约定的情形不赔付"]
            }
        }
    )


class InterpretationResponse(BaseModel):
    """
    Response model for insurance contract interpretation.

    Contains AI-generated analysis of insurance contract terms and conditions.
    """
    success: bool = Field(
        default=True,
        description="Indicates if the interpretation was successful"
    )
    summary: str = Field(
        ...,
        description="Brief summary of the insurance contract"
    )
    key_terms: List[ContractTerm] = Field(
        ...,
        description="Important terms and their explanations"
    )
    activation_conditions: List[PayoutCondition] = Field(
        ...,
        description="Conditions that activate the insurance coverage"
    )
    payout_details: PayoutDetails = Field(
        ...,
        description="Detailed information about payouts"
    )
    important_notes: List[str] = Field(
        default_factory=list,
        description="Important notes and warnings about the contract"
    )
    suggested_questions: List[str] = Field(
        default_factory=list,
        description="Questions to ask the insurance provider"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "summary": "这是一份重疾险保险合同，保额50万元，保障期限终身，缴费期20年。",
                "key_terms": [
                    {
                        "term": "等待期",
                        "explanation": "投保后90天内发生的疾病，保险公司不承担赔偿责任",
                        "importance": "critical"
                    }
                ],
                "activation_conditions": [
                    {
                        "condition": "确诊合同约定的重大疾病",
                        "description": "被保险人经医院确诊初次发生合同约定的重大疾病",
                        "required_documents": ["诊断证明书", "病历资料"]
                    }
                ],
                "payout_details": {
                    "payout_method": "一次性给付",
                    "payout_amount": "基本保额50万元",
                    "payout_timeline": "审核通过后10个工作日内"
                },
                "important_notes": [
                    "注意等待期90天",
                    "如实告知健康状况",
                    "按时缴纳保费"
                ],
                "suggested_questions": [
                    "具体保障哪些重大疾病？",
                    "等待期后是否立刻生效？",
                    "是否有轻症赔付？"
                ]
            }
        }
    )
