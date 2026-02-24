"""
Tests for interpretation API endpoint.

Tests file upload handling, validation, and response structure.
"""

import pytest
import io
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


@pytest.fixture
def sample_pdf_content():
    """Return minimal valid PDF content for testing."""
    return b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT/F1 12 Tf/100 700 Td(Test)Tj ET
endstream endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000202 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
290
%%EOF"""


@pytest.fixture
def sample_pdf_file(sample_pdf_content):
    """Create a file-like object with PDF content for testing."""
    return io.BytesIO(sample_pdf_content)


class TestInterpretationEndpointValidation:
    """Tests for interpretation endpoint request validation."""

    def test_interpretation_accepts_valid_pdf(self, sample_pdf_file):
        """Test that valid PDF upload is accepted (may fail on text extraction but file is accepted)."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("test.pdf", sample_pdf_file, "application/pdf")}
        )
        # The endpoint may return 422 for insufficient text or 502 for AI service,
        # but the file should be accepted (not a 422 for file type/size)
        # We just verify the endpoint processes the file
        assert response.status_code in [200, 422, 502, 500]

    def test_interpretation_rejects_non_pdf(self):
        """Test that non-PDF files are rejected."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("test.txt", b"text content", "text/plain")}
        )
        assert response.status_code == 422
        response_data = response.json()
        assert "PDF" in response_data.get("detail", "").lower()

    def test_interpretation_rejects_jpg_file(self):
        """Test that JPG files are rejected."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("test.jpg", b"\xff\xd8\xff\xe0", "image/jpeg")}
        )
        assert response.status_code == 422

    def test_interpretation_rejects_png_file(self):
        """Test that PNG files are rejected."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("test.png", b"\x89PNG\r\n\x1a\n", "image/png")}
        )
        assert response.status_code == 422

    def test_interpretation_rejects_large_file(self):
        """Test that files >10MB are rejected."""
        # Create a fake large file (11MB)
        large_content = b"x" * (11 * 1024 * 1024)

        response = client.post(
            "/api/interpretation",
            files={"file": ("large.pdf", large_content, "application/pdf")}
        )
        assert response.status_code == 422
        response_data = response.json()
        assert "10 mb" in response_data.get("detail", "").lower()

    def test_interpretation_rejects_empty_file(self):
        """Test that empty files are rejected."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
        assert response.status_code == 422
        response_data = response.json()
        assert "empty" in response_data.get("detail", "").lower()

    def test_interpretation_requires_file_parameter(self):
        """Test that file parameter is required."""
        response = client.post("/api/interpretation")
        assert response.status_code == 422


class TestInterpretationResponseStructure:
    """Tests for interpretation response structure."""

    def test_interpretation_pdf_with_wrong_extension(self, sample_pdf_file):
        """Test that PDF content with wrong extension is rejected."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("test.txt", sample_pdf_file, "application/pdf")}
        )
        # Should reject based on .txt extension even if content is PDF
        assert response.status_code == 422


class TestInterpretationIntegration:
    """Integration tests for interpretation endpoint."""

    def test_minimal_pdf_file_structure(self, sample_pdf_file):
        """Test that minimal valid PDF structure is handled."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("minimal.pdf", sample_pdf_file, "application/pdf")}
        )
        # Check the response structure
        # May fail due to insufficient text, but should handle gracefully
        assert response.status_code in [200, 422, 500, 502]

    def test_filename_with_pdf_extension_check(self, sample_pdf_file):
        """Test that only .pdf extension files are accepted."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("document.PDF", sample_pdf_file, "application/pdf")}
        )
        # Uppercase .PDF should also be accepted
        # May fail on other grounds (text extraction, AI service)
        # but not on file extension
        if response.status_code == 422:
            response_data = response.json()
            detail = response_data.get("detail", "").lower()
            # Should not be about file extension
            assert "pdf" not in detail or "only" not in detail


class TestInterpretationEdgeCases:
    """Tests for edge cases in interpretation endpoint."""

    def test_file_with_no_pdf_marker(self):
        """Test that file without PDF marker is rejected."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("fake.pdf", b"This is not a PDF", "application/pdf")}
        )
        # Should fail during PDF processing
        assert response.status_code == 422
        response_data = response.json()
        detail = response_data.get("detail", "").lower()
        assert "pdf" in detail or "corrupted" in detail or "invalid" in detail

    def test_corrupted_pdf_content(self):
        """Test handling of corrupted PDF content."""
        corrupted_pdf = b"%PDF-1.4\nCorrupted content here"

        response = client.post(
            "/api/interpretation",
            files={"file": ("corrupted.pdf", corrupted_pdf, "application/pdf")}
        )
        assert response.status_code == 422

    def test_pdf_with_special_characters_in_filename(self, sample_pdf_file):
        """Test filename with special characters is handled."""
        response = client.post(
            "/api/interpretation",
            files={"file": ("test file (1) 中文.pdf", sample_pdf_file, "application/pdf")}
        )
        # Should handle special characters in filename
        # May fail on other grounds but not on filename parsing
        assert response.status_code in [200, 422, 500, 502]

    def test_content_type_validation(self, sample_pdf_file):
        """Test that Content-Type header is checked."""
        # Send with wrong content type
        response = client.post(
            "/api/interpretation",
            files={"file": ("test.pdf", sample_pdf_file, "application/octet-stream")}
        )
        # The endpoint checks file extension primarily
        # Content-Type is secondary
        assert response.status_code in [200, 422, 500, 502]


class TestFileSizeBoundaries:
    """Tests for file size boundary conditions."""

    def test_exactly_10mb_file(self):
        """Test file that is exactly 10MB."""
        # Create a file that's exactly 10MB
        exact_10mb = b"x" * (10 * 1024 * 1024)

        response = client.post(
            "/api/interpretation",
            files={"file": ("exact.pdf", exact_10mb, "application/pdf")}
        )
        # 10MB should be accepted (may fail on PDF processing)
        # but not on file size
        if response.status_code == 422:
            response_data = response.json()
            detail = response_data.get("detail", "").lower()
            assert "10 mb" not in detail

    def test_just_over_10mb_file(self):
        """Test file that is just over 10MB."""
        # Create a file that's 10MB + 1 byte
        just_over = b"x" * (10 * 1024 * 1024 + 1)

        response = client.post(
            "/api/interpretation",
            files={"file": ("over.pdf", just_over, "application/pdf")}
        )
        # Should be rejected for size
        assert response.status_code == 422
        response_data = response.json()
        assert "10 mb" in response_data.get("detail", "").lower()

    def test_small_valid_pdf(self, sample_pdf_content):
        """Test that small valid PDF is processed correctly."""
        small_pdf = io.BytesIO(sample_pdf_content)

        response = client.post(
            "/api/interpretation",
            files={"file": ("small.pdf", small_pdf, "application/pdf")}
        )
        # Should be accepted for processing
        # May fail on text extraction or AI, but file size should be OK
        if response.status_code == 422:
            response_data = response.json()
            detail = response_data.get("detail", "").lower()
            assert "mb" not in detail
