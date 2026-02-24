"""
Interpretation API Endpoint

Handles insurance contract interpretation requests with file upload support.
"""

import json
from typing import List
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import ValidationError

from backend.app.models.responses import (
    InterpretationResponse,
    ContractTerm,
    PayoutCondition,
    PayoutDetails,
)
from backend.app.services.ai_service import AIService, AISettings
from backend.app.services.pdf_service import PDFService


# Create FastAPI router for interpretation endpoints
router = APIRouter(
    prefix="/api",
    tags=["interpretation"],
)

# Initialize AI service (loaded from environment variables)
_ai_service = None
_pdf_service = None


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


def get_pdf_service() -> PDFService:
    """
    Get or initialize the PDF service singleton.

    Returns:
        PDFService: The initialized PDF service instance.
    """
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService()
    return _pdf_service


@router.post(
    "/interpretation",
    response_model=InterpretationResponse,
    summary="Interpret insurance contract",
    description="Upload an insurance contract PDF and receive AI-powered analysis of key terms, coverage, and conditions",
)
async def interpret_contract(file: UploadFile = File(...)) -> InterpretationResponse:
    """
    Analyze an insurance contract PDF and provide structured interpretation.

    This endpoint accepts a PDF file of an insurance contract, extracts text content,
    and uses AI to provide detailed analysis including:
    - Contract summary and overview
    - Key terms and their plain-language explanations
    - Conditions that activate insurance coverage
    - Detailed payout information
    - Important notes and warnings
    - Suggested questions for the insurance provider

    Args:
        file: UploadFile object containing the insurance contract PDF.

    Returns:
        InterpretationResponse: Structured contract analysis with key terms,
                                conditions, and recommendations.

    Raises:
        HTTPException: If file validation, PDF parsing, or AI service fails.
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only PDF files are supported. Please upload a .pdf file."
            )

        # Read file content
        file_content = await file.read()

        # Validate file size (max 10 MB)
        max_file_size = 10 * 1024 * 1024  # 10 MB
        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File size exceeds maximum limit of 10 MB. Your file is {len(file_content) / (1024*1024):.2f} MB."
            )

        # Validate file is not empty
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file is empty. Please provide a valid PDF file."
            )

        # Get PDF service
        pdf_service = get_pdf_service()

        # Extract text from PDF
        try:
            contract_text = pdf_service.extract_text(file_content=file_content)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process PDF file: {str(e)}"
            )

        # Validate extracted text
        if not contract_text or len(contract_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract sufficient text from the PDF. The file may be image-based or corrupted."
            )

        # Get AI service
        ai_service = get_ai_service()

        # Call AI service for contract interpretation
        ai_analysis = await ai_service.interpret_contract(contract_text)

        # Parse AI analysis into structured response
        summary = _extract_summary(ai_analysis)
        key_terms = _parse_key_terms(ai_analysis)
        activation_conditions = _parse_activation_conditions(ai_analysis)
        payout_details = _parse_payout_details(ai_analysis)
        important_notes = _extract_important_notes(ai_analysis)
        suggested_questions = _extract_suggested_questions(ai_analysis)

        return InterpretationResponse(
            success=True,
            summary=summary,
            key_terms=key_terms,
            activation_conditions=activation_conditions,
            payout_details=payout_details,
            important_notes=important_notes,
            suggested_questions=suggested_questions,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle AI service or PDF service errors
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Service error: {str(e)}"
        )
    except ValidationError as e:
        # Handle response validation errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Response validation failed: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred: {str(e)}"
        )


def _extract_summary(ai_analysis: dict) -> str:
    """
    Extract contract summary from AI analysis.

    Args:
        ai_analysis: Dictionary containing AI-generated contract analysis.

    Returns:
        Contract summary string.
    """
    summary = ai_analysis.get("summary", "")

    if not summary:
        # Fallback: Try to construct summary from other fields
        coverage = ai_analysis.get("coverage_details", {})
        if coverage:
            scope = coverage.get("scope", "")
            amount = coverage.get("coverage_amount", "")
            period = coverage.get("coverage_period", "")
            summary_parts = [scope, amount, period]
            summary = " | ".join([s for s in summary_parts if s])
        else:
            summary = "保险合同分析已完成。请查看详细条款解读。"

    return summary


def _parse_key_terms(ai_analysis: dict) -> List[ContractTerm]:
    """
    Parse key terms from AI analysis into ContractTerm objects.

    Args:
        ai_analysis: Dictionary containing AI-generated contract analysis.

    Returns:
        List of ContractTerm objects.
    """
    terms = []

    # Try to extract key_terms from analysis
    key_terms_data = ai_analysis.get("key_terms", [])
    important_clauses = ai_analysis.get("important_clauses", [])

    # Process key_terms
    for term_data in key_terms_data:
        if isinstance(term_data, dict):
            term_name = term_data.get("term", term_data.get("name", ""))
            definition = term_data.get("definition", term_data.get("explanation", ""))

            if term_name:
                # Determine importance based on content
                importance = _determine_term_importance(term_name, definition)

                terms.append(ContractTerm(
                    term=term_name,
                    explanation=definition or "暂无解释",
                    importance=importance,
                ))

    # Process important_clauses if no key_terms found
    if not terms and important_clauses:
        for clause_data in important_clauses:
            if isinstance(clause_data, dict):
                clause_name = clause_data.get("clause", "")
                clause_content = clause_data.get("content", "")
                importance = clause_data.get("importance", "medium")

                # Map importance to standard values
                if importance not in ["critical", "high", "medium", "low"]:
                    if "关键" in str(importance) or "重要" in str(importance):
                        importance = "high"
                    else:
                        importance = "medium"

                if clause_name:
                    terms.append(ContractTerm(
                        term=clause_name,
                        explanation=clause_content or "重要条款",
                        importance=importance,
                    ))

    # If no terms found, add a default term
    if not terms:
        terms.append(ContractTerm(
            term="保险责任",
            explanation="请仔细阅读合同中的保险责任条款，了解保险公司在何种情况下承担赔偿责任",
            importance="critical",
        ))

    return terms


def _determine_term_importance(term_name: str, definition: str) -> str:
    """
    Determine the importance level of a contract term.

    Args:
        term_name: Name of the term.
        definition: Definition/explanation of the term.

    Returns:
        Importance level: 'critical', 'high', 'medium', or 'low'.
    """
    critical_keywords = ["等待期", "免责", "除外", "观察期", "自杀", "欺诈"]
    high_keywords = ["保险期间", "保险金额", "保额", "缴费", "犹豫期", "宽限期"]

    term_lower = term_name.lower()
    definition_lower = definition.lower()

    for keyword in critical_keywords:
        if keyword in term_name or keyword in definition:
            return "critical"

    for keyword in high_keywords:
        if keyword in term_name or keyword in definition:
            return "high"

    return "medium"


def _parse_activation_conditions(ai_analysis: dict) -> List[PayoutCondition]:
    """
    Parse activation/payout conditions from AI analysis.

    Args:
        ai_analysis: Dictionary containing AI-generated contract analysis.

    Returns:
        List of PayoutCondition objects.
    """
    conditions = []

    # Try to extract from coverage_details
    coverage_details = ai_analysis.get("coverage_details", {})

    # Extract coverage scope as a condition
    scope = coverage_details.get("scope", "")
    if scope:
        conditions.append(PayoutCondition(
            condition="保险保障范围",
            description=scope,
            required_documents=None,
        ))

    # Look for payout triggers in recommendations or other fields
    recommendations = ai_analysis.get("recommendations", [])
    for rec in recommendations:
        if isinstance(rec, dict):
            point = rec.get("point", "")
            if any(keyword in point for keyword in ["理赔", "赔付", "申请", "触发"]):
                conditions.append(PayoutCondition(
                    condition=point[:50],  # Limit length
                    description=rec.get("reason", ""),
                    required_documents=None,
                ))

    # If no conditions found, add a default one
    if not conditions:
        coverage_amount = coverage_details.get("coverage_amount", "")
        conditions.append(PayoutCondition(
            condition="保险事故发生",
            description=f"合同约定的保险事故发生时，保险公司按约定进行赔付。{coverage_amount}",
            required_documents=["保险合同", "身份证明", "事故证明"],
        ))

    return conditions


def _parse_payout_details(ai_analysis: dict) -> PayoutDetails:
    """
    Parse payout details from AI analysis.

    Args:
        ai_analysis: Dictionary containing AI-generated contract analysis.

    Returns:
        PayoutDetails object.
    """
    coverage_details = ai_analysis.get("coverage_details", {})

    payout_method = "按合同约定"
    payout_amount = coverage_details.get("coverage_amount", "按合同约定")
    payout_timeline = coverage_details.get("coverage_period", "按合同约定")

    # Try to extract more detailed payout information
    obligations = ai_analysis.get("obligations", [])
    limitations = []

    for obl in obligations:
        if isinstance(obl, dict):
            obligation_text = obl.get("obligation", "")
            description = obl.get("description", "")
            if "限制" in obligation_text or "除外" in obligation_text:
                limitations.append(f"{obligation_text}: {description}")

    # Add exclusions to limitations
    exclusions = ai_analysis.get("exclusions", [])
    for excl in exclusions:
        if isinstance(excl, dict):
            item = excl.get("item", "")
            description = excl.get("description", "")
            limitations.append(f"{item}: {description}")

    return PayoutDetails(
        payout_method=payout_method,
        payout_amount=payout_amount,
        payout_timeline=payout_timeline,
        limitations=limitations if limitations else None,
    )


def _extract_important_notes(ai_analysis: dict) -> List[str]:
    """
    Extract important notes from AI analysis.

    Args:
        ai_analysis: Dictionary containing AI-generated contract analysis.

    Returns:
        List of important note strings.
    """
    notes = []

    # Extract from recommendations
    recommendations = ai_analysis.get("recommendations", [])
    for rec in recommendations[:5]:  # Limit to 5 recommendations
        if isinstance(rec, dict):
            point = rec.get("point", "")
            reason = rec.get("reason", "")
            if point:
                note = f"{point}"
                if reason:
                    note += f" - {reason}"
                notes.append(note[:200])  # Limit length

    # Add exclusions as important notes
    exclusions = ai_analysis.get("exclusions", [])
    for excl in exclusions[:3]:  # Limit to 3 exclusions
        if isinstance(excl, dict):
            item = excl.get("item", "")
            if item:
                notes.append(f"免责条款：{item}"[:200])

    # Remove duplicates while preserving order
    seen = set()
    unique_notes = []
    for note in notes:
        if note not in seen:
            seen.add(note)
            unique_notes.append(note)

    return unique_notes[:8]  # Limit to 8 notes


def _extract_suggested_questions(ai_analysis: dict) -> List[str]:
    """
    Extract suggested questions from AI analysis.

    Args:
        ai_analysis: Dictionary containing AI-generated contract analysis.

    Returns:
        List of suggested question strings.
    """
    questions = []

    # Extract from important_clauses
    important_clauses = ai_analysis.get("important_clauses", [])
    for clause in important_clauses[:3]:
        if isinstance(clause, dict):
            clause_name = clause.get("clause", "")
            if clause_name:
                questions.append(f"关于{clause_name}的具体规定是什么？")

    # Default questions if none extracted
    if not questions:
        questions = [
            "等待期是多久？等待期内发生疾病是否赔付？",
            "具体保障哪些重大疾病或意外情况？",
            "理赔需要提供哪些材料？",
            "是否有免责条款？具体内容是什么？",
        ]

    return questions[:5]  # Limit to 5 questions
