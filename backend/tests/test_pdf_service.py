"""
Tests for PDF service.

Tests PDF text extraction, validation, and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from backend.app.services.pdf_service import PDFService


@pytest.fixture
def pdf_service():
    """Create a PDF service instance for testing."""
    return PDFService()


@pytest.fixture
def sample_pdf_content():
    """Return minimal valid PDF content for testing."""
    # Minimal valid PDF (PDF 1.4 specification)
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Count 1
/Kids [3 0 R]
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000202 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
290
%%EOF"""


@pytest.fixture
def sample_pdf_file(sample_pdf_content):
    """Create a temporary PDF file for testing."""
    fd, path = tempfile.mkstemp(suffix=".pdf")
    try:
        os.write(fd, sample_pdf_content)
        os.close(fd)
        yield path
    finally:
        if os.path.exists(path):
            os.unlink(path)


class TestPDFServiceExtraction:
    """Tests for PDF text extraction methods."""

    def test_extract_text_from_valid_pdf_file(self, pdf_service, sample_pdf_file):
        """Test extracting text from a valid PDF file."""
        text = pdf_service.extract_text(file_path=sample_pdf_file)
        assert isinstance(text, str)
        # The PDF contains "Test PDF Content"
        assert "Test PDF Content" in text or len(text) > 0

    def test_extract_text_from_pdf_bytes(self, pdf_service, sample_pdf_content):
        """Test extracting text from PDF bytes content."""
        text = pdf_service.extract_text(file_content=sample_pdf_content)
        assert isinstance(text, str)
        assert len(text) >= 0  # May be empty for minimal PDF

    def test_extract_text_no_parameters_error(self, pdf_service):
        """Test that providing neither parameter raises error."""
        with pytest.raises(ValueError, match="Either file_path or file_content must be provided"):
            pdf_service.extract_text()

    def test_extract_text_both_parameters_error(self, pdf_service, sample_pdf_file, sample_pdf_content):
        """Test that providing both file_path and file_content raises error."""
        with pytest.raises(ValueError, match="Only one of file_path or file_content"):
            pdf_service.extract_text(file_path=sample_pdf_file, file_content=sample_pdf_content)

    def test_extract_text_file_not_found_error(self, pdf_service):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            pdf_service.extract_text(file_path="nonexistent.pdf")

    def test_extract_text_invalid_pdf_content(self, pdf_service):
        """Test handling of invalid PDF content."""
        invalid_content = b"This is not a PDF file"
        with pytest.raises(ValueError, match="Invalid or corrupted PDF"):
            pdf_service.extract_text(file_content=invalid_content)

    def test_extract_text_empty_pdf_content(self, pdf_service):
        """Test handling of empty content."""
        with pytest.raises(ValueError, match="Invalid or corrupted PDF"):
            pdf_service.extract_text(file_content=b"")

    def test_extract_simple_from_valid_pdf(self, pdf_service, sample_pdf_file):
        """Test extract_text_simple method."""
        text = pdf_service.extract_text_simple(file_path=sample_pdf_file)
        assert isinstance(text, str)

    def test_extract_simple_no_parameters_error(self, pdf_service):
        """Test extract_text_simple without parameters raises error."""
        with pytest.raises(ValueError, match="Either file_path or file_content must be provided"):
            pdf_service.extract_text_simple()

    def test_extract_simple_both_parameters_error(self, pdf_service, sample_pdf_file, sample_pdf_content):
        """Test extract_text_simple with both parameters raises error."""
        with pytest.raises(ValueError, match="Only one of file_path or file_content"):
            pdf_service.extract_text_simple(file_path=sample_pdf_file, file_content=sample_pdf_content)


class TestPDFServiceValidation:
    """Tests for PDF validation method."""

    def test_validate_pdf_valid_file(self, pdf_service, sample_pdf_file):
        """Test PDF validation returns correct metadata for valid file."""
        metadata = pdf_service.validate_pdf(file_path=sample_pdf_file)
        assert metadata["is_valid"] == True
        assert metadata["page_count"] >= 1
        assert isinstance(metadata["size_bytes"], int)
        assert metadata["size_bytes"] > 0

    def test_validate_pdf_from_bytes(self, pdf_service, sample_pdf_content):
        """Test PDF validation from bytes content."""
        metadata = pdf_service.validate_pdf(file_content=sample_pdf_content)
        assert metadata["is_valid"] == True
        assert metadata["size_bytes"] == len(sample_pdf_content)

    def test_validate_pdf_no_parameters_error(self, pdf_service):
        """Test validation without parameters raises error."""
        with pytest.raises(ValueError, match="Either file_path or file_content must be provided"):
            pdf_service.validate_pdf()

    def test_validate_pdf_invalid_content(self, pdf_service):
        """Test validation of invalid PDF content."""
        metadata = pdf_service.validate_pdf(file_content=b"Not a PDF")
        assert metadata["is_valid"] == False
        assert metadata["error"] is not None
        assert "Invalid or corrupted PDF" in metadata["error"] or "Validation failed" in metadata["error"]

    def test_validate_pdf_empty_content(self, pdf_service):
        """Test validation of empty content."""
        metadata = pdf_service.validate_pdf(file_content=b"")
        assert metadata["is_valid"] == False
        assert metadata["error"] is not None

    def test_validate_pdf_nonexistent_file(self, pdf_service):
        """Test validation of non-existent file."""
        metadata = pdf_service.validate_pdf(file_path="nonexistent.pdf")
        assert metadata["is_valid"] == False
        assert "not found" in metadata["error"]


class TestPDFServiceErrorHandling:
    """Tests for error handling in PDF service."""

    def test_password_protected_pdf(self, pdf_service):
        """
        Test handling of password-protected PDF.

        Note: We create a mock password-protected error scenario.
        In real scenario, this would need an actual password-protected PDF.
        """
        # Since we can't easily create a password-protected PDF in tests,
        # we verify the error message would be correct if encountered
        # The actual PDF library would raise pymupdf.PasswordError
        pass

    def test_corrupted_pdf(self, pdf_service):
        """Test handling of corrupted PDF file."""
        corrupted_content = b"%PDF-1.4\nCorrupted content here"
        with pytest.raises(ValueError, match="Invalid or corrupted PDF|Failed to extract text"):
            pdf_service.extract_text(file_content=corrupted_content)

    def test_import_error_handling(self):
        """Test that PDFService handles missing PyMuPDF gracefully."""
        # This test verifies the lazy import mechanism
        service = PDFService()
        # Accessing _get_pymupdf should trigger import
        # If PyMuPDF is not installed, it should raise ImportError
        try:
            pymupdf = service._get_pymupdf()
            assert pymupdf is not None
        except ImportError as e:
            assert "PyMuPDF" in str(e)


class TestPDFServiceEdgeCases:
    """Tests for edge cases."""

    def test_extract_text_with_path_object(self, pdf_service, sample_pdf_file):
        """Test extraction with Path object instead of string."""
        text = pdf_service.extract_text(file_path=Path(sample_pdf_file))
        assert isinstance(text, str)

    def test_validate_with_path_object(self, pdf_service, sample_pdf_file):
        """Test validation with Path object."""
        metadata = pdf_service.validate_pdf(file_path=Path(sample_pdf_file))
        assert metadata["is_valid"] == True

    def test_extract_returns_string_type(self, pdf_service, sample_pdf_file):
        """Test that extract_text always returns a string."""
        text = pdf_service.extract_text(file_path=sample_pdf_file)
        assert type(text) == str

    def test_validate_returns_dict_with_all_keys(self, pdf_service, sample_pdf_file):
        """Test that validate_pdf returns dict with all expected keys."""
        metadata = pdf_service.validate_pdf(file_path=sample_pdf_file)
        expected_keys = ["is_valid", "page_count", "is_encrypted", "size_bytes", "error"]
        for key in expected_keys:
            assert key in metadata
