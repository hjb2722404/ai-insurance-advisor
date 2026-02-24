"""
Tests for consultation API endpoint.

Tests request validation, Pydantic model validation, and API responses.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.requests import ConsultationRequest, GenderEnum, MaritalStatusEnum

client = TestClient(app)


def test_consultation_valid_request():
    """Test that valid consultation request structure is accepted."""
    # This test verifies the request structure is valid
    # Note: Actual API call would require OPENAI_API_KEY to be set
    request = ConsultationRequest(
        name="张三",
        age=35,
        gender=GenderEnum.MALE,
        occupation="软件工程师",
        annual_income=500000,
        marital_status=MaritalStatusEnum.MARRIED,
        num_dependents=2
    )
    assert request.name == "张三"
    assert request.age == 35
    assert request.gender == GenderEnum.MALE
    assert request.occupation == "软件工程师"
    assert request.annual_income == 500000
    assert request.marital_status == MaritalStatusEnum.MARRIED
    assert request.num_dependents == 2


def test_consultation_missing_required_field():
    """Test that missing required fields are rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 35
        # Missing: gender, occupation, annual_income, marital_status
    })
    assert response.status_code == 422


def test_consultation_invalid_age():
    """Test that invalid age is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 200,  # Invalid age (>150)
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": 500000,
        "marital_status": "married"
    })
    assert response.status_code == 422


def test_consultation_negative_age():
    """Test that negative age is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": -1,  # Invalid age (<0)
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": 500000,
        "marital_status": "married"
    })
    assert response.status_code == 422


def test_consultation_invalid_gender():
    """Test that invalid gender enum is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 35,
        "gender": "invalid",  # Invalid gender
        "occupation": "软件工程师",
        "annual_income": 500000,
        "marital_status": "married"
    })
    assert response.status_code == 422


def test_consultation_invalid_marital_status():
    """Test that invalid marital status enum is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 35,
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": 500000,
        "marital_status": "invalid"  # Invalid marital status
    })
    assert response.status_code == 422


def test_consultation_negative_income():
    """Test that negative income is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 35,
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": -1000,  # Invalid income
        "marital_status": "married"
    })
    assert response.status_code == 422


def test_consultation_unreasonable_income():
    """Test that unreasonably high income is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 35,
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": 2_000_000_000,  # Over 1 billion
        "marital_status": "married"
    })
    assert response.status_code == 422


def test_consultation_too_many_dependents():
    """Test that too many dependents is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 35,
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": 500000,
        "marital_status": "married",
        "num_dependents": 25  # Over 20
    })
    assert response.status_code == 422


def test_consultation_pydantic_model_validation():
    """Test Pydantic model validates required fields."""
    # Valid request
    request = ConsultationRequest(
        name="张三",
        age=35,
        gender=GenderEnum.MALE,
        occupation="软件工程师",
        annual_income=500000,
        marital_status=MaritalStatusEnum.MARRIED
    )
    assert request.name == "张三"
    assert request.age == 35

    # Missing required field should raise error
    with pytest.raises(Exception):
        ConsultationRequest(
            name="张三"
            # Missing required fields: age, gender, occupation, annual_income, marital_status
        )


def test_consultation_optional_fields():
    """Test that optional fields work correctly."""
    request = ConsultationRequest(
        name="李四",
        age=28,
        gender=GenderEnum.FEMALE,
        occupation="医生",
        annual_income=600000,
        marital_status=MaritalStatusEnum.SINGLE
    )
    assert request.health_conditions is None
    assert request.existing_insurance is None
    assert request.additional_notes is None


def test_consultation_with_optional_fields():
    """Test consultation with optional fields populated."""
    request = ConsultationRequest(
        name="王五",
        age=40,
        gender=GenderEnum.MALE,
        occupation="教师",
        annual_income=400000,
        marital_status=MaritalStatusEnum.MARRIED,
        num_dependents=1,
        health_conditions=["高血压"],
        existing_insurance=["社会保险", "商业医疗险"],
        additional_notes="希望增加重疾险保障"
    )
    assert request.health_conditions == ["高血压"]
    assert request.existing_insurance == ["社会保险", "商业医疗险"]
    assert request.additional_notes == "希望增加重疾险保障"


def test_consultation_empty_lists_converted_to_none():
    """Test that empty lists are converted to None."""
    request = ConsultationRequest(
        name="赵六",
        age=30,
        gender=GenderEnum.OTHER,
        occupation="设计师",
        annual_income=450000,
        marital_status=MaritalStatusEnum.DIVORCED,
        health_conditions=[],
        existing_insurance=[]
    )
    assert request.health_conditions is None
    assert request.existing_insurance is None


def test_consultation_name_too_long():
    """Test that name exceeding max length is rejected."""
    response = client.post("/api/consultation", json={
        "name": "a" * 101,  # Over 100 characters
        "age": 35,
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": 500000,
        "marital_status": "married"
    })
    assert response.status_code == 422


def test_consultation_name_whitespace_stripped():
    """Test that whitespace is stripped from name."""
    request = ConsultationRequest(
        name="  张三  ",
        age=35,
        gender=GenderEnum.MALE,
        occupation="软件工程师",
        annual_income=500000,
        marital_status=MaritalStatusEnum.MARRIED
    )
    assert request.name == "张三"


def test_consultation_additional_notes_too_long():
    """Test that additional notes exceeding max length is rejected."""
    response = client.post("/api/consultation", json={
        "name": "张三",
        "age": 35,
        "gender": "male",
        "occupation": "软件工程师",
        "annual_income": 500000,
        "marital_status": "married",
        "additional_notes": "a" * 1001  # Over 1000 characters
    })
    assert response.status_code == 422


def test_all_gender_enum_values():
    """Test all valid gender enum values."""
    for gender_value in [GenderEnum.MALE, GenderEnum.FEMALE, GenderEnum.OTHER]:
        request = ConsultationRequest(
            name="测试",
            age=30,
            gender=gender_value,
            occupation="测试职业",
            annual_income=500000,
            marital_status=MaritalStatusEnum.SINGLE
        )
        assert request.gender == gender_value


def test_all_marital_status_enum_values():
    """Test all valid marital status enum values."""
    for status_value in [MaritalStatusEnum.SINGLE, MaritalStatusEnum.MARRIED,
                          MaritalStatusEnum.DIVORCED, MaritalStatusEnum.WIDOWED]:
        request = ConsultationRequest(
            name="测试",
            age=30,
            gender=GenderEnum.MALE,
            occupation="测试职业",
            annual_income=500000,
            marital_status=status_value
        )
        assert request.marital_status == status_value
