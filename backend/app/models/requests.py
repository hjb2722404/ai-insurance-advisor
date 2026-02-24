"""
Request Models

Pydantic models for validating incoming API requests.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class GenderEnum(str, Enum):
    """Gender options for consultation request."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MaritalStatusEnum(str, Enum):
    """Marital status options for consultation request."""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class ConsultationRequest(BaseModel):
    """
    Request model for insurance plan consultation.

    Contains user and family information for generating personalized
    insurance recommendations.
    """
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    age: int = Field(..., ge=0, le=150, description="User's age in years")
    gender: GenderEnum = Field(..., description="User's gender")
    occupation: str = Field(..., min_length=1, max_length=100, description="User's occupation")
    annual_income: float = Field(..., ge=0, description="Annual income in local currency")
    marital_status: MaritalStatusEnum = Field(..., description="User's marital status")
    num_dependents: int = Field(
        default=0,
        ge=0,
        le=20,
        description="Number of dependents (children, elderly parents, etc.)"
    )
    health_conditions: Optional[List[str]] = Field(
        default=None,
        description="List of existing health conditions or disabilities"
    )
    existing_insurance: Optional[List[str]] = Field(
        default=None,
        description="List of existing insurance policies"
    )
    additional_notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Any additional information or specific requirements"
    )

    @field_validator("health_conditions", "existing_insurance", mode="before")
    @classmethod
    def empty_list_to_none(cls, v):
        """Convert empty lists to None for cleaner API responses."""
        if v == []:
            return None
        return v

    @field_validator("annual_income")
    @classmethod
    def income_must_be_reasonable(cls, v: float) -> float:
        """Validate that income is within reasonable bounds."""
        if v > 1_000_000_000:  # 1 billion
            raise ValueError("Annual income seems unreasonably high")
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "张三",
                "age": 35,
                "gender": "male",
                "occupation": "软件工程师",
                "annual_income": 500000,
                "marital_status": "married",
                "num_dependents": 2,
                "health_conditions": None,
                "existing_insurance": ["社会保险"],
                "additional_notes": "希望增加重疾险保障"
            }
        }
    )
