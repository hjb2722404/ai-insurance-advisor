"""
PDF Service

Handles PDF document parsing and text extraction using PyMuPDF
for insurance contract interpretation.
"""

import io
from typing import Optional, Union
from pathlib import Path


class PDFService:
    """
    Service for extracting text from PDF documents.

    Provides methods for parsing insurance contract PDFs
    and extracting text content for AI analysis.
    """

    def __init__(self) -> None:
        """
        Initialize the PDF service.

        Note: PyMuPDF (pymupdf) is imported lazily to avoid
        import errors if the package is not installed.
        """
        self._pymupdf = None

    def _get_pymupdf(self):
        """
        Lazy import of PyMuPDF module.

        Returns:
            The pymupdf module.

        Raises:
            ImportError: If PyMuPDF is not installed.
        """
        if self._pymupdf is None:
            try:
                import pymupdf
                self._pymupdf = pymupdf
            except ImportError as e:
                raise ImportError(
                    "PyMuPDF is not installed. "
                    "Install it with: pip install PyMuPDF"
                ) from e
        return self._pymupdf

    def extract_text(
        self,
        file_path: Optional[Union[str, Path]] = None,
        file_content: Optional[bytes] = None
    ) -> str:
        """
        Extract text from a PDF document.

        Supports extraction from either a file path or raw file content bytes.
        Handles corrupted, password-protected, and image-only PDFs gracefully.

        Args:
            file_path: Path to the PDF file. Optional if file_content is provided.
            file_content: Raw bytes of the PDF file. Optional if file_path is provided.

        Returns:
            Extracted text content from the PDF as a string.

        Raises:
            ValueError: If neither file_path nor file_content is provided,
                       or if the file cannot be processed.
            FileNotFoundError: If file_path is provided but file doesn't exist.
        """
        if file_path is None and file_content is None:
            raise ValueError(
                "Either file_path or file_content must be provided"
            )

        if file_path is not None and file_content is not None:
            raise ValueError(
                "Only one of file_path or file_content should be provided, not both"
            )

        pymupdf = self._get_pymupdf()

        try:
            doc = None

            if file_path is not None:
                # Open PDF from file path
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"PDF file not found: {file_path}")

                doc = pymupdf.open(str(path))

            else:
                # Open PDF from bytes content
                doc = pymupdf.open(stream=file_content)

            # Extract text from all pages
            text_content = self._extract_text_from_doc(doc)

            # Close the document
            doc.close()

            return text_content

        except FileNotFoundError:
            raise
        except PermissionError as e:
            raise ValueError(
                f"Permission denied accessing PDF file: {str(e)}"
            ) from e
        except pymupdf.FileDataError as e:
            raise ValueError(
                f"Invalid or corrupted PDF file: {str(e)}"
            ) from e
        except pymupdf.PasswordError as e:
            raise ValueError(
                "PDF file is password-protected and cannot be opened. "
                "Please provide an unprotected PDF."
            ) from e
        except Exception as e:
            raise ValueError(
                f"Failed to extract text from PDF: {str(e)}"
            ) from e

    def _extract_text_from_doc(self, doc) -> str:
        """
        Extract text content from a PyMuPDF document object.

        Args:
            doc: PyMuPDF document object.

        Returns:
            Extracted text content as a string.
        """
        text_parts = []

        for page_num, page in enumerate(doc):
            # Extract text blocks from the page
            # get_text("blocks") returns a list of blocks
            # Each block is a tuple: (x0, y0, x1, y1, text, block_no, block_type)
            blocks = page.get_text("blocks")

            for block in blocks:
                # block[6] indicates if the block contains text (not an image)
                if block[6]:
                    # block[4] is the text content
                    text = block[4]
                    if text.strip():  # Only add non-empty text
                        text_parts.append(text.strip())

            # Add page separator for better readability
            if text_parts:
                text_parts.append("\n")

        return "\n".join(text_parts)

    def extract_text_simple(
        self,
        file_path: Optional[Union[str, Path]] = None,
        file_content: Optional[bytes] = None
    ) -> str:
        """
        Extract text from PDF using simple extraction method.

        This is an alternative method that extracts all text at once
        without preserving block structure. Simpler but potentially
        less accurate formatting.

        Args:
            file_path: Path to the PDF file. Optional if file_content is provided.
            file_content: Raw bytes of the PDF file. Optional if file_path is provided.

        Returns:
            Extracted text content from the PDF as a string.

        Raises:
            ValueError: If neither file_path nor file_content is provided,
                       or if the file cannot be processed.
            FileNotFoundError: If file_path is provided but file doesn't exist.
        """
        if file_path is None and file_content is None:
            raise ValueError(
                "Either file_path or file_content must be provided"
            )

        if file_path is not None and file_content is not None:
            raise ValueError(
                "Only one of file_path or file_content should be provided, not both"
            )

        pymupdf = self._get_pymupdf()

        try:
            doc = None

            if file_path is not None:
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"PDF file not found: {file_path}")
                doc = pymupdf.open(str(path))
            else:
                doc = pymupdf.open(stream=file_content)

            # Get all text at once
            text = doc.get_text()

            doc.close()

            return text

        except FileNotFoundError:
            raise
        except pymupdf.FileDataError as e:
            raise ValueError(
                f"Invalid or corrupted PDF file: {str(e)}"
            ) from e
        except pymupdf.PasswordError as e:
            raise ValueError(
                "PDF file is password-protected and cannot be opened. "
                "Please provide an unprotected PDF."
            ) from e
        except Exception as e:
            raise ValueError(
                f"Failed to extract text from PDF: {str(e)}"
            ) from e

    def validate_pdf(
        self,
        file_path: Optional[Union[str, Path]] = None,
        file_content: Optional[bytes] = None
    ) -> dict:
        """
        Validate a PDF file and extract metadata.

        Checks if the file is a valid PDF and returns metadata
        such as page count, file size, and whether it's password-protected.

        Args:
            file_path: Path to the PDF file. Optional if file_content is provided.
            file_content: Raw bytes of the PDF file. Optional if file_path is provided.

        Returns:
            Dictionary containing PDF metadata with keys:
            - is_valid: Boolean indicating if the file is a valid PDF
            - page_count: Number of pages in the PDF
            - is_encrypted: Boolean indicating if PDF is password-protected
            - size_bytes: File size in bytes
            - error: Error message if validation failed, None otherwise

        Raises:
            ValueError: If neither file_path nor file_content is provided.
        """
        if file_path is None and file_content is None:
            raise ValueError(
                "Either file_path or file_content must be provided"
            )

        result = {
            "is_valid": False,
            "page_count": 0,
            "is_encrypted": False,
            "size_bytes": 0,
            "error": None
        }

        pymupdf = self._get_pymupdf()

        try:
            doc = None

            if file_path is not None:
                path = Path(file_path)
                result["size_bytes"] = path.stat().st_size
                if not path.exists():
                    result["error"] = f"PDF file not found: {file_path}"
                    return result
                doc = pymupdf.open(str(path))
            else:
                result["size_bytes"] = len(file_content)
                doc = pymupdf.open(stream=file_content)

            result["is_valid"] = True
            result["page_count"] = doc.page_count
            result["is_encrypted"] = doc.is_encrypted

            doc.close()

        except pymupdf.FileDataError as e:
            result["error"] = f"Invalid or corrupted PDF: {str(e)}"
        except pymupdf.PasswordError:
            result["is_encrypted"] = True
            result["error"] = "PDF is password-protected"
        except Exception as e:
            result["error"] = f"Validation failed: {str(e)}"

        return result
