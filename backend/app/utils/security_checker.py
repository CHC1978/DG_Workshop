"""Security Checker Utility

Comprehensive security audit tool to verify system security configurations
and detect potential anomalies.

Usage:
    python -m app.utils.security_checker
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.user import User, UserRole
from app.models.equipment import Equipment
from app.models.equipment_log import EquipmentLog


class CheckStatus(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    INFO = "INFO"


@dataclass
class CheckResult:
    """Result of a security check"""
    name: str
    status: CheckStatus
    message: str
    details: list[str] = field(default_factory=list)


class SecurityChecker:
    """Comprehensive security checker for the application"""

    def __init__(self):
        self.results: list[CheckResult] = []
        # Convert async sqlite URL to sync for this utility
        db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

    def add_result(self, name: str, status: CheckStatus, message: str, details: list[str] = None):
        """Add a check result"""
        self.results.append(CheckResult(
            name=name,
            status=status,
            message=message,
            details=details or []
        ))

    def close(self):
        """Close database session"""
        self.db.close()

    # ==================== Configuration Checks ====================

    def check_secret_key(self):
        """Verify SECRET_KEY is not default or weak"""
        weak_keys = [
            "your-secret-key-here",
            "secret",
            "changeme",
            "development",
            "test",
        ]

        if not settings.SECRET_KEY:
            self.add_result(
                "SECRET_KEY Configuration",
                CheckStatus.FAIL,
                "SECRET_KEY is not set"
            )
        elif settings.SECRET_KEY.lower() in weak_keys or len(settings.SECRET_KEY) < 32:
            self.add_result(
                "SECRET_KEY Configuration",
                CheckStatus.FAIL,
                "SECRET_KEY is weak or default value",
                ["Use a cryptographically secure random string of at least 32 characters"]
            )
        else:
            self.add_result(
                "SECRET_KEY Configuration",
                CheckStatus.PASS,
                f"SECRET_KEY is properly configured (length: {len(settings.SECRET_KEY)})"
            )

    def check_cookie_security(self):
        """Verify cookie security settings"""
        issues = []

        if not settings.SECURE_COOKIE:
            issues.append("SECURE_COOKIE is disabled (cookies not sent over HTTPS only)")

        if settings.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
            issues.append(f"ACCESS_TOKEN_EXPIRE_MINUTES={settings.ACCESS_TOKEN_EXPIRE_MINUTES} is too long (recommended: 30-60)")

        if issues:
            self.add_result(
                "Cookie Security",
                CheckStatus.WARN,
                "Cookie security issues found",
                issues
            )
        else:
            self.add_result(
                "Cookie Security",
                CheckStatus.PASS,
                "Cookie security settings are properly configured"
            )

    def check_cors_settings(self):
        """Check CORS configuration"""
        cors_origins = settings.BACKEND_CORS_ORIGINS
        if "*" in cors_origins:
            self.add_result(
                "CORS Configuration",
                CheckStatus.WARN,
                "CORS allows all origins (*)",
                ["Consider restricting to specific domains in production"]
            )
        else:
            self.add_result(
                "CORS Configuration",
                CheckStatus.PASS,
                f"CORS is restricted to {len(cors_origins)} origin(s)"
            )

    # ==================== User Security Checks ====================

    def check_users_without_2fa(self):
        """Check for users without 2FA enabled"""
        users_without_2fa = self.db.query(User).filter(
            User.totp_enabled == False,
            User.is_active == True
        ).all()

        if users_without_2fa:
            user_list = [f"{u.username} ({u.role.value})" for u in users_without_2fa]

            # Check if any are admin/manager
            privileged = [u for u in users_without_2fa if u.role in [UserRole.ADMIN, UserRole.MANAGER]]

            if privileged:
                self.add_result(
                    "2FA Coverage",
                    CheckStatus.FAIL,
                    f"Found {len(privileged)} privileged user(s) without 2FA",
                    [f"{u.username} ({u.role.value})" for u in privileged]
                )
            else:
                self.add_result(
                    "2FA Coverage",
                    CheckStatus.WARN,
                    f"Found {len(users_without_2fa)} user(s) without 2FA",
                    user_list[:10]  # Show first 10
                )
        else:
            self.add_result(
                "2FA Coverage",
                CheckStatus.PASS,
                "All active users have 2FA enabled"
            )

    def check_inactive_users(self):
        """Check for inactive users that might need attention"""
        inactive_users = self.db.query(User).filter(
            User.is_active == False
        ).count()

        self.add_result(
            "Inactive Users",
            CheckStatus.INFO,
            f"Found {inactive_users} inactive user(s)",
            ["Consider reviewing and removing if no longer needed"] if inactive_users > 10 else []
        )

    def check_admin_count(self):
        """Check number of admin users"""
        admin_count = self.db.query(User).filter(
            User.role == UserRole.ADMIN,
            User.is_active == True
        ).count()

        if admin_count == 0:
            self.add_result(
                "Admin Users",
                CheckStatus.FAIL,
                "No active admin users found"
            )
        elif admin_count > 3:
            self.add_result(
                "Admin Users",
                CheckStatus.WARN,
                f"Found {admin_count} admin users (consider limiting admin privileges)",
                ["Follow principle of least privilege"]
            )
        else:
            self.add_result(
                "Admin Users",
                CheckStatus.PASS,
                f"Found {admin_count} admin user(s)"
            )

    # ==================== Database Security Checks ====================

    def check_database_file(self):
        """Check database file security"""
        # Extract path from various sqlite URL formats
        db_url = settings.DATABASE_URL
        db_path = db_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")

        if not os.path.exists(db_path):
            self.add_result(
                "Database File",
                CheckStatus.WARN,
                f"Database file not found: {db_path}"
            )
            return

        # Check if database is in a secure location
        if "data" not in db_path.lower():
            self.add_result(
                "Database Location",
                CheckStatus.WARN,
                "Database file is not in the 'data' directory",
                ["Consider moving to a dedicated data directory"]
            )
        else:
            self.add_result(
                "Database Location",
                CheckStatus.PASS,
                "Database file is in the data directory"
            )

        # Check file size
        file_size = os.path.getsize(db_path)
        size_mb = file_size / (1024 * 1024)

        self.add_result(
            "Database Size",
            CheckStatus.INFO,
            f"Database size: {size_mb:.2f} MB"
        )

    # ==================== Audit Trail Checks ====================

    def check_recent_suspicious_logs(self):
        """Check for suspicious patterns in equipment logs"""
        one_day_ago = datetime.now() - timedelta(days=1)

        # Check for high volume of changes from single user
        high_volume_users = self.db.query(
            EquipmentLog.created_by,
            func.count(EquipmentLog.id).label('count')
        ).filter(
            EquipmentLog.created_at >= one_day_ago,
            EquipmentLog.created_by.isnot(None)
        ).group_by(
            EquipmentLog.created_by
        ).having(
            func.count(EquipmentLog.id) > 100
        ).all()

        if high_volume_users:
            details = [f"User ID {user_id}: {count} changes" for user_id, count in high_volume_users]
            self.add_result(
                "High Volume Activity",
                CheckStatus.WARN,
                f"Found {len(high_volume_users)} user(s) with >100 changes in 24h",
                details
            )
        else:
            self.add_result(
                "High Volume Activity",
                CheckStatus.PASS,
                "No unusual high-volume activity detected"
            )

        # Check for bulk status changes
        status_changes = self.db.query(
            EquipmentLog
        ).filter(
            EquipmentLog.created_at >= one_day_ago,
            EquipmentLog.log_type == "status_change"
        ).count()

        if status_changes > 50:
            self.add_result(
                "Bulk Status Changes",
                CheckStatus.WARN,
                f"Found {status_changes} status changes in 24h",
                ["Review if this is expected activity"]
            )
        else:
            self.add_result(
                "Bulk Status Changes",
                CheckStatus.PASS,
                f"Found {status_changes} status changes in 24h (normal)"
            )

    def check_edited_logs(self):
        """Check for edited log entries"""
        edited_logs = self.db.query(EquipmentLog).filter(
            EquipmentLog.edit_count > 0
        ).count()

        heavily_edited = self.db.query(EquipmentLog).filter(
            EquipmentLog.edit_count > 3
        ).count()

        if heavily_edited > 0:
            self.add_result(
                "Edited Logs",
                CheckStatus.WARN,
                f"Found {heavily_edited} log(s) edited more than 3 times",
                ["Review these entries for potential tampering"]
            )
        elif edited_logs > 0:
            self.add_result(
                "Edited Logs",
                CheckStatus.INFO,
                f"Found {edited_logs} edited log entries (normal corrections)"
            )
        else:
            self.add_result(
                "Edited Logs",
                CheckStatus.PASS,
                "No edited log entries found"
            )

    # ==================== File Security Checks ====================

    def check_upload_directory(self):
        """Check upload directory security"""
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")

        if not os.path.exists(upload_dir):
            self.add_result(
                "Upload Directory",
                CheckStatus.INFO,
                "Upload directory does not exist yet"
            )
            return

        # Count files by type
        file_counts = {}
        total_size = 0
        suspicious_files = []

        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                file_counts[ext] = file_counts.get(ext, 0) + 1

                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)

                # Check for suspicious extensions
                if ext in ['.exe', '.bat', '.sh', '.ps1', '.cmd', '.php', '.jsp']:
                    suspicious_files.append(file)

        if suspicious_files:
            self.add_result(
                "Suspicious Files",
                CheckStatus.FAIL,
                f"Found {len(suspicious_files)} suspicious file(s) in uploads",
                suspicious_files[:10]
            )
        else:
            size_mb = total_size / (1024 * 1024)
            self.add_result(
                "Upload Directory",
                CheckStatus.PASS,
                f"Upload directory OK ({len(file_counts)} file types, {size_mb:.2f} MB total)"
            )

    # ==================== Rate Limiting Checks ====================

    def check_rate_limiting_config(self):
        """Verify rate limiting is configured"""
        # Check if limiter is imported in main
        main_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "main.py"
        )

        try:
            with open(main_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if "slowapi" in content and "limiter" in content:
                self.add_result(
                    "Rate Limiting",
                    CheckStatus.PASS,
                    "Rate limiting (slowapi) is configured"
                )
            else:
                self.add_result(
                    "Rate Limiting",
                    CheckStatus.WARN,
                    "Rate limiting may not be properly configured"
                )
        except Exception as e:
            self.add_result(
                "Rate Limiting",
                CheckStatus.WARN,
                f"Could not verify rate limiting: {e}"
            )

    # ==================== CSRF Checks ====================

    def check_csrf_protection(self):
        """Verify CSRF protection is configured"""
        csrf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "core", "csrf.py"
        )

        if os.path.exists(csrf_path):
            self.add_result(
                "CSRF Protection",
                CheckStatus.PASS,
                "CSRF protection module exists"
            )
        else:
            self.add_result(
                "CSRF Protection",
                CheckStatus.FAIL,
                "CSRF protection module not found"
            )

    # ==================== Run All Checks ====================

    def run_all_checks(self):
        """Run all security checks"""
        print("\n" + "=" * 60)
        print("  Security Audit Report")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")

        # Configuration checks
        print("[Configuration Checks]")
        self.check_secret_key()
        self.check_cookie_security()
        self.check_cors_settings()
        self.check_rate_limiting_config()
        self.check_csrf_protection()

        # User security checks
        print("\n[User Security Checks]")
        self.check_users_without_2fa()
        self.check_inactive_users()
        self.check_admin_count()

        # Database checks
        print("\n[Database Checks]")
        self.check_database_file()

        # Audit trail checks
        print("\n[Audit Trail Checks]")
        self.check_recent_suspicious_logs()
        self.check_edited_logs()

        # File security checks
        print("\n[File Security Checks]")
        self.check_upload_directory()

        # Print results
        self._print_results()

        # Summary
        self._print_summary()

        self.close()

    def _print_results(self):
        """Print all check results"""
        status_symbols = {
            CheckStatus.PASS: "[PASS]",
            CheckStatus.WARN: "[WARN]",
            CheckStatus.FAIL: "[FAIL]",
            CheckStatus.INFO: "[INFO]"
        }

        status_colors = {
            CheckStatus.PASS: "\033[92m",  # Green
            CheckStatus.WARN: "\033[93m",  # Yellow
            CheckStatus.FAIL: "\033[91m",  # Red
            CheckStatus.INFO: "\033[94m",  # Blue
        }
        reset = "\033[0m"

        current_category = None
        for result in self.results:
            color = status_colors.get(result.status, "")
            symbol = status_symbols.get(result.status, "[????]")

            print(f"  {color}{symbol}{reset} {result.name}")
            print(f"         {result.message}")

            for detail in result.details:
                print(f"           - {detail}")

    def _print_summary(self):
        """Print summary of all checks"""
        counts = {
            CheckStatus.PASS: 0,
            CheckStatus.WARN: 0,
            CheckStatus.FAIL: 0,
            CheckStatus.INFO: 0
        }

        for result in self.results:
            counts[result.status] += 1

        print("\n" + "=" * 60)
        print("  Summary")
        print("=" * 60)
        print(f"  \033[92mPASS: {counts[CheckStatus.PASS]}\033[0m")
        print(f"  \033[93mWARN: {counts[CheckStatus.WARN]}\033[0m")
        print(f"  \033[91mFAIL: {counts[CheckStatus.FAIL]}\033[0m")
        print(f"  \033[94mINFO: {counts[CheckStatus.INFO]}\033[0m")
        print(f"  Total: {len(self.results)}")

        if counts[CheckStatus.FAIL] > 0:
            print("\n  \033[91m[!] Critical issues found - immediate action required\033[0m")
        elif counts[CheckStatus.WARN] > 0:
            print("\n  \033[93m[!] Warnings found - review recommended\033[0m")
        else:
            print("\n  \033[92m[+] All checks passed\033[0m")

        print()


def main():
    """Main entry point"""
    checker = SecurityChecker()
    checker.run_all_checks()


if __name__ == "__main__":
    main()
