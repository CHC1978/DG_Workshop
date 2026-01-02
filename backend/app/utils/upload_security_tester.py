"""Upload Security Tester

Security testing tool for file upload validation.
Tests magic number verification, fake extension detection, and PDF security scanning.

Usage:
    cd backend
    ./venv/Scripts/python -m app.utils.upload_security_tester
"""

import io
import sys
import os
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.file_validator import (
    FileValidator,
    ValidationStatus,
    ValidationResult,
    FileType,
    validate_upload,
)


class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str
    details: List[str] = None


class UploadSecurityTester:
    """Security tester for file upload validation"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.validator = FileValidator()

    def add_result(self, name: str, status: TestStatus, message: str, details: List[str] = None):
        self.results.append(TestResult(
            name=name,
            status=status,
            message=message,
            details=details or []
        ))

    # ==================== Test Data Generators ====================

    def _create_valid_jpeg(self) -> bytes:
        """Create a minimal valid JPEG file"""
        # Minimal JPEG structure
        return (
            b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            b'\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9444'
            b'\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00'
            b'\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b'
            b'\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\x7F\xFF\xD9'
        )

    def _create_valid_png(self) -> bytes:
        """Create a minimal valid PNG file"""
        return (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR'  # IHDR chunk
            b'\x00\x00\x00\x01'    # width: 1
            b'\x00\x00\x00\x01'    # height: 1
            b'\x08\x02'            # bit depth: 8, color type: 2 (RGB)
            b'\x00\x00\x00'        # compression, filter, interlace
            b'\x90wS\xde'          # CRC
            b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def _create_valid_pdf(self) -> bytes:
        """Create a minimal valid PDF file"""
        return (
            b'%PDF-1.4\n'
            b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
            b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
            b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n'
            b'xref\n0 4\n'
            b'0000000000 65535 f \n'
            b'0000000009 00000 n \n'
            b'0000000058 00000 n \n'
            b'0000000115 00000 n \n'
            b'trailer\n<< /Size 4 /Root 1 0 R >>\n'
            b'startxref\n193\n%%EOF'
        )

    def _create_pdf_with_javascript(self) -> bytes:
        """Create a PDF with JavaScript (malicious)"""
        return (
            b'%PDF-1.4\n'
            b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R /OpenAction 4 0 R >>\nendobj\n'
            b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
            b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n'
            b'4 0 obj\n<< /Type /Action /S /JavaScript /JS (app.alert("XSS")) >>\nendobj\n'
            b'xref\n0 5\n'
            b'trailer\n<< /Size 5 /Root 1 0 R >>\n'
            b'startxref\n300\n%%EOF'
        )

    def _create_pdf_with_launch(self) -> bytes:
        """Create a PDF with Launch action (malicious)"""
        return (
            b'%PDF-1.4\n'
            b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R /OpenAction 4 0 R >>\nendobj\n'
            b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
            b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n'
            b'4 0 obj\n<< /Type /Action /S /Launch /F (cmd.exe) >>\nendobj\n'
            b'xref\n0 5\n'
            b'trailer\n<< /Size 5 /Root 1 0 R >>\n'
            b'startxref\n300\n%%EOF'
        )

    def _create_image_with_script(self) -> bytes:
        """Create a JPEG with embedded script in comment"""
        jpeg = self._create_valid_jpeg()
        # Insert a comment with script
        script_comment = b'\xFF\xFE\x00\x20<script>alert("XSS")</script>'
        # Insert after JFIF APP0 marker
        return jpeg[:20] + script_comment + jpeg[20:]

    # ==================== Tests ====================

    def test_valid_jpeg_detection(self):
        """Test that valid JPEG files are correctly detected"""
        content = self._create_valid_jpeg()
        result = self.validator.validate_file(content, "image", "test.jpg")

        if result.status == ValidationStatus.VALID and result.file_type == FileType.JPEG:
            self.add_result(
                "Valid JPEG Detection",
                TestStatus.PASS,
                "Valid JPEG correctly identified"
            )
        else:
            self.add_result(
                "Valid JPEG Detection",
                TestStatus.FAIL,
                f"Failed: status={result.status.value}, type={result.file_type.value}"
            )

    def test_valid_png_detection(self):
        """Test that valid PNG files are correctly detected"""
        content = self._create_valid_png()
        result = self.validator.validate_file(content, "image", "test.png")

        if result.status == ValidationStatus.VALID and result.file_type == FileType.PNG:
            self.add_result(
                "Valid PNG Detection",
                TestStatus.PASS,
                "Valid PNG correctly identified"
            )
        else:
            self.add_result(
                "Valid PNG Detection",
                TestStatus.FAIL,
                f"Failed: status={result.status.value}, type={result.file_type.value}"
            )

    def test_valid_pdf_detection(self):
        """Test that valid PDF files are correctly detected"""
        content = self._create_valid_pdf()
        result = self.validator.validate_file(content, "pdf", "test.pdf")

        if result.status == ValidationStatus.VALID and result.file_type == FileType.PDF:
            self.add_result(
                "Valid PDF Detection",
                TestStatus.PASS,
                "Valid PDF correctly identified"
            )
        else:
            self.add_result(
                "Valid PDF Detection",
                TestStatus.FAIL,
                f"Failed: status={result.status.value}, type={result.file_type.value}"
            )

    def test_fake_extension_detection(self):
        """Test detection of files with fake extensions"""
        # Create a valid JPEG but try to pass it as PDF
        jpeg_content = self._create_valid_jpeg()
        result = self.validator.validate_file(jpeg_content, "pdf", "fake.pdf")

        if result.status == ValidationStatus.INVALID_SIGNATURE:
            self.add_result(
                "Fake Extension Detection",
                TestStatus.PASS,
                "Fake extension correctly rejected"
            )
        else:
            self.add_result(
                "Fake Extension Detection",
                TestStatus.FAIL,
                f"Fake extension not detected: status={result.status.value}",
                ["A JPEG file with .pdf extension should be rejected"]
            )

    def test_unknown_file_type(self):
        """Test handling of unknown file types"""
        # Random bytes that don't match any known signature
        random_content = b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99'
        result = self.validator.validate_file(random_content, "image", "unknown.bin")

        if result.status == ValidationStatus.INVALID_SIGNATURE:
            self.add_result(
                "Unknown File Type",
                TestStatus.PASS,
                "Unknown file type correctly rejected"
            )
        else:
            self.add_result(
                "Unknown File Type",
                TestStatus.FAIL,
                f"Unknown file type not rejected: status={result.status.value}"
            )

    def test_pdf_javascript_detection(self):
        """Test detection of JavaScript in PDF files"""
        content = self._create_pdf_with_javascript()
        result = self.validator.validate_file(content, "pdf", "malicious.pdf")

        if result.status == ValidationStatus.SUSPICIOUS_CONTENT:
            self.add_result(
                "PDF JavaScript Detection",
                TestStatus.PASS,
                "PDF with JavaScript correctly flagged as suspicious",
                result.warnings
            )
        else:
            self.add_result(
                "PDF JavaScript Detection",
                TestStatus.FAIL,
                f"PDF with JavaScript not detected: status={result.status.value}"
            )

    def test_pdf_launch_detection(self):
        """Test detection of Launch action in PDF files"""
        content = self._create_pdf_with_launch()
        result = self.validator.validate_file(content, "pdf", "malicious.pdf")

        if result.status == ValidationStatus.SUSPICIOUS_CONTENT:
            self.add_result(
                "PDF Launch Action Detection",
                TestStatus.PASS,
                "PDF with Launch action correctly flagged as suspicious",
                result.warnings
            )
        else:
            self.add_result(
                "PDF Launch Action Detection",
                TestStatus.FAIL,
                f"PDF with Launch action not detected: status={result.status.value}"
            )

    def test_image_script_detection(self):
        """Test detection of script content in image files"""
        content = self._create_image_with_script()
        result = self.validator.validate_file(content, "image", "malicious.jpg")

        if result.status == ValidationStatus.SUSPICIOUS_CONTENT:
            self.add_result(
                "Image Script Detection",
                TestStatus.PASS,
                "Image with embedded script correctly flagged",
                result.warnings
            )
        else:
            self.add_result(
                "Image Script Detection",
                TestStatus.FAIL,
                f"Image with script not detected: status={result.status.value}"
            )

    def test_image_sanitization(self):
        """Test image sanitization functionality"""
        try:
            from PIL import Image

            # Create a simple image with metadata
            img = Image.new('RGB', (10, 10), color='red')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            original_content = buffer.getvalue()

            # Sanitize
            sanitized_content, success = self.validator.sanitize_image(original_content)

            if success and len(sanitized_content) > 0:
                # Verify sanitized image is valid
                sanitized_img = Image.open(io.BytesIO(sanitized_content))
                if sanitized_img.size == (10, 10):
                    self.add_result(
                        "Image Sanitization",
                        TestStatus.PASS,
                        "Image successfully sanitized"
                    )
                else:
                    self.add_result(
                        "Image Sanitization",
                        TestStatus.FAIL,
                        "Sanitized image has wrong dimensions"
                    )
            else:
                self.add_result(
                    "Image Sanitization",
                    TestStatus.FAIL,
                    "Image sanitization failed"
                )
        except ImportError:
            self.add_result(
                "Image Sanitization",
                TestStatus.SKIP,
                "Pillow not installed - skipping image sanitization test"
            )
        except Exception as e:
            self.add_result(
                "Image Sanitization",
                TestStatus.FAIL,
                f"Image sanitization error: {e}"
            )

    def test_validate_upload_function(self):
        """Test the convenience validate_upload function"""
        content = self._create_valid_jpeg()
        processed, result = validate_upload(content, "test.jpg", "image", sanitize=False)

        if result.status == ValidationStatus.VALID and len(processed) > 0:
            self.add_result(
                "validate_upload Function",
                TestStatus.PASS,
                "validate_upload function works correctly"
            )
        else:
            self.add_result(
                "validate_upload Function",
                TestStatus.FAIL,
                f"validate_upload failed: status={result.status.value}"
            )

    def test_empty_file_handling(self):
        """Test handling of empty files"""
        result = self.validator.validate_file(b'', "image", "empty.jpg")

        if result.status == ValidationStatus.INVALID_SIGNATURE:
            self.add_result(
                "Empty File Handling",
                TestStatus.PASS,
                "Empty file correctly rejected"
            )
        else:
            self.add_result(
                "Empty File Handling",
                TestStatus.FAIL,
                f"Empty file not rejected: status={result.status.value}"
            )

    def test_truncated_file_handling(self):
        """Test handling of truncated files"""
        # Just the magic number, nothing else
        truncated = b'\xFF\xD8\xFF'
        result = self.validator.validate_file(truncated, "image", "truncated.jpg")

        # Should still detect as JPEG but may warn
        if result.file_type == FileType.JPEG:
            self.add_result(
                "Truncated File Handling",
                TestStatus.PASS,
                "Truncated file correctly identified by magic number"
            )
        else:
            self.add_result(
                "Truncated File Handling",
                TestStatus.FAIL,
                f"Truncated file handling issue: type={result.file_type.value}"
            )

    # ==================== Run All Tests ====================

    def run_all_tests(self):
        """Run all security tests"""
        print("\n" + "=" * 60)
        print("  Upload Security Test Report")
        print("=" * 60 + "\n")

        # Magic Number Tests
        print("[Magic Number Validation Tests]")
        self.test_valid_jpeg_detection()
        self.test_valid_png_detection()
        self.test_valid_pdf_detection()

        # Fake Extension Tests
        print("\n[Fake Extension Detection Tests]")
        self.test_fake_extension_detection()
        self.test_unknown_file_type()

        # PDF Security Tests
        print("\n[PDF Security Scanning Tests]")
        self.test_pdf_javascript_detection()
        self.test_pdf_launch_detection()

        # Image Security Tests
        print("\n[Image Security Tests]")
        self.test_image_script_detection()
        self.test_image_sanitization()

        # Edge Cases
        print("\n[Edge Case Tests]")
        self.test_validate_upload_function()
        self.test_empty_file_handling()
        self.test_truncated_file_handling()

        # Print results
        self._print_results()
        self._print_summary()

    def _print_results(self):
        """Print all test results"""
        status_symbols = {
            TestStatus.PASS: "\033[92m[PASS]\033[0m",
            TestStatus.FAIL: "\033[91m[FAIL]\033[0m",
            TestStatus.SKIP: "\033[93m[SKIP]\033[0m",
        }

        for result in self.results:
            symbol = status_symbols.get(result.status, "[????]")
            print(f"  {symbol} {result.name}")
            print(f"         {result.message}")

            if result.details:
                for detail in result.details:
                    print(f"           - {detail}")

    def _print_summary(self):
        """Print test summary"""
        counts = {
            TestStatus.PASS: 0,
            TestStatus.FAIL: 0,
            TestStatus.SKIP: 0,
        }

        for result in self.results:
            counts[result.status] += 1

        print("\n" + "=" * 60)
        print("  Summary")
        print("=" * 60)
        print(f"  \033[92mPASS: {counts[TestStatus.PASS]}\033[0m")
        print(f"  \033[91mFAIL: {counts[TestStatus.FAIL]}\033[0m")
        print(f"  \033[93mSKIP: {counts[TestStatus.SKIP]}\033[0m")
        print(f"  Total: {len(self.results)}")

        if counts[TestStatus.FAIL] > 0:
            print("\n  \033[91m[!] Some tests failed - review the issues above\033[0m")
        elif counts[TestStatus.SKIP] > 0:
            print("\n  \033[93m[!] Some tests skipped - check dependencies\033[0m")
        else:
            print("\n  \033[92m[+] All tests passed\033[0m")

        print()


def main():
    """Main entry point"""
    tester = UploadSecurityTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
