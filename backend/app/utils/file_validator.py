"""File Validator Utility

Comprehensive file validation for secure file uploads.
Includes magic number verification, image sanitization, and PDF security scanning.

Usage:
    from app.utils.file_validator import FileValidator

    validator = FileValidator()
    result = validator.validate_file(file_path, expected_type="image")
"""

import io
import logging
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types"""
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    WEBP = "image/webp"
    PDF = "application/pdf"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    UNKNOWN = "unknown"


class ValidationStatus(Enum):
    """Validation result status"""
    VALID = "valid"
    INVALID_SIGNATURE = "invalid_signature"
    SUSPICIOUS_CONTENT = "suspicious_content"
    MALFORMED = "malformed"
    SANITIZED = "sanitized"


@dataclass
class ValidationResult:
    """Result of file validation"""
    status: ValidationStatus
    file_type: FileType
    message: str
    warnings: List[str] = field(default_factory=list)
    sanitized: bool = False


# File signatures (Magic Numbers)
# Format: (signature_bytes, offset, file_type)
FILE_SIGNATURES = [
    # Images
    (b'\xFF\xD8\xFF', 0, FileType.JPEG),           # JPEG
    (b'\x89PNG\r\n\x1a\n', 0, FileType.PNG),       # PNG
    (b'GIF87a', 0, FileType.GIF),                   # GIF87a
    (b'GIF89a', 0, FileType.GIF),                   # GIF89a
    # WEBP: RIFF....WEBP
    (b'RIFF', 0, FileType.WEBP),                    # WEBP (partial, need further check)
    # Documents
    (b'%PDF', 0, FileType.PDF),                     # PDF
    (b'PK\x03\x04', 0, FileType.DOCX),             # DOCX (ZIP-based)
    (b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1', 0, FileType.DOC),  # DOC (OLE)
]

# PDF dangerous patterns
PDF_DANGEROUS_PATTERNS = [
    (b'/JavaScript', "JavaScript code detected"),
    (b'/JS', "JavaScript reference detected"),
    (b'/OpenAction', "Auto-open action detected"),
    (b'/AA', "Additional actions detected"),
    (b'/Launch', "Launch action detected (can execute programs)"),
    (b'/EmbeddedFile', "Embedded file detected"),
    (b'/RichMedia', "Rich media content detected"),
    (b'/XFA', "XFA form detected (potential security risk)"),
]


class FileValidator:
    """Comprehensive file validator for secure uploads"""

    def __init__(self, sanitize_images: bool = True):
        """
        Initialize the file validator.

        Args:
            sanitize_images: Whether to sanitize (re-encode) images to remove metadata
        """
        self.sanitize_images = sanitize_images

    def validate_file(
        self,
        file_content: bytes,
        expected_type: str,
        filename: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a file's content and type.

        Args:
            file_content: The file content as bytes
            expected_type: Expected file type ("image", "pdf", "document")
            filename: Optional filename for logging

        Returns:
            ValidationResult with status and details
        """
        # Detect file type from magic number
        detected_type = self._detect_file_type(file_content)

        if detected_type == FileType.UNKNOWN:
            return ValidationResult(
                status=ValidationStatus.INVALID_SIGNATURE,
                file_type=FileType.UNKNOWN,
                message="Unable to detect file type from signature"
            )

        # Validate based on expected type
        if expected_type == "image":
            return self._validate_image(file_content, detected_type, filename)
        elif expected_type == "pdf":
            return self._validate_pdf(file_content, detected_type, filename)
        elif expected_type == "document":
            return self._validate_document(file_content, detected_type, filename)
        else:
            return ValidationResult(
                status=ValidationStatus.VALID,
                file_type=detected_type,
                message=f"File validated as {detected_type.value}"
            )

    def _detect_file_type(self, content: bytes) -> FileType:
        """Detect file type from magic number signature."""
        for signature, offset, file_type in FILE_SIGNATURES:
            if len(content) > offset + len(signature):
                if content[offset:offset + len(signature)] == signature:
                    # Special check for WEBP
                    if file_type == FileType.WEBP:
                        if len(content) >= 12 and content[8:12] == b'WEBP':
                            return FileType.WEBP
                        continue
                    return file_type
        return FileType.UNKNOWN

    def _validate_image(
        self,
        content: bytes,
        detected_type: FileType,
        filename: Optional[str]
    ) -> ValidationResult:
        """Validate and optionally sanitize an image file."""
        # Check if it's actually an image type
        image_types = [FileType.JPEG, FileType.PNG, FileType.GIF, FileType.WEBP]
        if detected_type not in image_types:
            return ValidationResult(
                status=ValidationStatus.INVALID_SIGNATURE,
                file_type=detected_type,
                message=f"Expected image but detected {detected_type.value}"
            )

        warnings = []

        # Check for suspicious patterns in image files
        # Some attacks embed scripts in image metadata or comments
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'<?php',
            b'<%',
            b'eval(',
        ]

        for pattern in suspicious_patterns:
            if pattern.lower() in content.lower():
                logger.warning(f"Suspicious pattern found in image: {pattern}")
                warnings.append(f"Suspicious pattern detected: {pattern.decode('utf-8', errors='ignore')}")

        if warnings:
            return ValidationResult(
                status=ValidationStatus.SUSPICIOUS_CONTENT,
                file_type=detected_type,
                message="Image contains suspicious content",
                warnings=warnings
            )

        return ValidationResult(
            status=ValidationStatus.VALID,
            file_type=detected_type,
            message=f"Image validated as {detected_type.value}"
        )

    def _validate_pdf(
        self,
        content: bytes,
        detected_type: FileType,
        filename: Optional[str]
    ) -> ValidationResult:
        """Validate a PDF file for dangerous content."""
        if detected_type != FileType.PDF:
            return ValidationResult(
                status=ValidationStatus.INVALID_SIGNATURE,
                file_type=detected_type,
                message=f"Expected PDF but detected {detected_type.value}"
            )

        warnings = []

        # Check for dangerous patterns
        for pattern, description in PDF_DANGEROUS_PATTERNS:
            if pattern in content:
                logger.warning(f"PDF security warning ({filename}): {description}")
                warnings.append(description)

        if warnings:
            # Determine severity
            critical_patterns = [b'/JavaScript', b'/JS', b'/Launch']
            has_critical = any(p in content for p in critical_patterns)

            if has_critical:
                return ValidationResult(
                    status=ValidationStatus.SUSPICIOUS_CONTENT,
                    file_type=detected_type,
                    message="PDF contains potentially dangerous content",
                    warnings=warnings
                )
            else:
                # Just warnings, not blocking
                return ValidationResult(
                    status=ValidationStatus.VALID,
                    file_type=detected_type,
                    message="PDF validated with warnings",
                    warnings=warnings
                )

        return ValidationResult(
            status=ValidationStatus.VALID,
            file_type=detected_type,
            message="PDF validated successfully"
        )

    def _validate_document(
        self,
        content: bytes,
        detected_type: FileType,
        filename: Optional[str]
    ) -> ValidationResult:
        """Validate a document file (DOC, DOCX)."""
        doc_types = [FileType.DOC, FileType.DOCX, FileType.PDF]
        if detected_type not in doc_types:
            return ValidationResult(
                status=ValidationStatus.INVALID_SIGNATURE,
                file_type=detected_type,
                message=f"Expected document but detected {detected_type.value}"
            )

        warnings = []

        # For DOCX (ZIP-based), check for macros
        if detected_type == FileType.DOCX:
            # Check for vbaProject.bin which indicates macros
            if b'vbaProject.bin' in content:
                warnings.append("Document contains VBA macros")
                logger.warning(f"DOCX with macros detected: {filename}")

            # Check for external relationships
            if b'Target="http' in content or b'Target="https' in content:
                warnings.append("Document contains external links")

        # For DOC (OLE), check for macros indicator
        if detected_type == FileType.DOC:
            # OLE documents with macros often contain these
            if b'_VBA_PROJECT' in content or b'VBA' in content:
                warnings.append("Document may contain VBA macros")
                logger.warning(f"DOC with potential macros detected: {filename}")

        if warnings:
            return ValidationResult(
                status=ValidationStatus.VALID,
                file_type=detected_type,
                message="Document validated with warnings",
                warnings=warnings
            )

        return ValidationResult(
            status=ValidationStatus.VALID,
            file_type=detected_type,
            message="Document validated successfully"
        )

    def sanitize_image(self, content: bytes, output_format: str = None) -> Tuple[bytes, bool]:
        """
        Sanitize an image by re-encoding it to remove metadata and potential malicious content.

        Args:
            content: Original image content
            output_format: Optional output format (JPEG, PNG, etc.)

        Returns:
            Tuple of (sanitized_content, success)
        """
        try:
            from PIL import Image

            # Open the image
            img = Image.open(io.BytesIO(content))

            # Get the format
            original_format = img.format or 'JPEG'
            target_format = output_format or original_format

            # Convert to RGB if necessary (for JPEG)
            if target_format.upper() == 'JPEG' and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Create new image without metadata
            # This effectively strips EXIF, comments, and other metadata
            data = list(img.getdata())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)

            # Save to bytes
            output = io.BytesIO()
            save_kwargs = {}

            if target_format.upper() == 'JPEG':
                save_kwargs['quality'] = 95
                save_kwargs['optimize'] = True
            elif target_format.upper() == 'PNG':
                save_kwargs['optimize'] = True
            elif target_format.upper() == 'WEBP':
                save_kwargs['quality'] = 95

            clean_img.save(output, format=target_format, **save_kwargs)

            logger.info(f"Image sanitized: {img.size[0]}x{img.size[1]} {target_format}")
            return output.getvalue(), True

        except Exception as e:
            logger.error(f"Failed to sanitize image: {e}")
            return content, False

    def get_image_info(self, content: bytes) -> Optional[dict]:
        """
        Get basic image information without full validation.

        Args:
            content: Image content

        Returns:
            Dict with width, height, format, mode or None if not an image
        """
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(content))
            return {
                "width": img.size[0],
                "height": img.size[1],
                "format": img.format,
                "mode": img.mode,
            }
        except Exception:
            return None


def validate_upload(
    file_content: bytes,
    filename: str,
    file_type: str,
    sanitize: bool = True
) -> Tuple[bytes, ValidationResult]:
    """
    Convenience function to validate and optionally sanitize an uploaded file.

    Args:
        file_content: The uploaded file content
        filename: Original filename
        file_type: Expected type ("image", "pdf", "document")
        sanitize: Whether to sanitize images

    Returns:
        Tuple of (processed_content, validation_result)
    """
    validator = FileValidator(sanitize_images=sanitize)
    result = validator.validate_file(file_content, file_type, filename)

    # If valid image and sanitization is enabled, sanitize it
    if (result.status == ValidationStatus.VALID and
        file_type == "image" and
        sanitize):
        sanitized_content, success = validator.sanitize_image(file_content)
        if success:
            result.sanitized = True
            return sanitized_content, result

    return file_content, result
