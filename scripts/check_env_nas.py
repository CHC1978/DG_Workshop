#!/usr/bin/env python
"""
Environment Configuration Check Script for NAS
Verifies that all critical settings are correctly configured.

Usage on NAS:
1. Copy to /volume1/docker/marine-equipment/
2. Run via Task Scheduler:
   docker cp /volume1/docker/marine-equipment/check_env_nas.py marine-equipment-backend:/app/
   docker exec marine-equipment-backend python check_env_nas.py
"""
from datetime import datetime


def check_environment():
    """Check and display current environment configuration"""
    from app.core.config import settings

    print("=" * 60)
    print("Environment Configuration Check")
    print("=" * 60)
    print(f"Check time: {datetime.now()}")
    print("")

    # Critical settings
    checks = []

    # Check QR_CODE_DOMAIN
    print("-" * 60)
    print("QR Code Settings:")
    print(f"  QR_CODE_DOMAIN:   {settings.QR_CODE_DOMAIN}")
    print(f"  QR_CODE_PROTOCOL: {settings.QR_CODE_PROTOCOL}")

    # Validate QR_CODE_DOMAIN has port if using non-standard
    domain = settings.QR_CODE_DOMAIN
    protocol = settings.QR_CODE_PROTOCOL

    if protocol == "https":
        if ":443" not in domain and ":" not in domain:
            checks.append(("WARNING", "QR_CODE_DOMAIN missing port for HTTPS (should include :8443 if non-standard)"))
        elif ":8443" in domain:
            checks.append(("OK", "QR_CODE_DOMAIN includes port :8443"))
        elif ":443" in domain:
            checks.append(("OK", "QR_CODE_DOMAIN uses standard HTTPS port 443"))
        elif ":" in domain:
            port = domain.split(":")[-1]
            checks.append(("OK", f"QR_CODE_DOMAIN includes port :{port}"))
    elif protocol == "http":
        if ":80" not in domain and ":" not in domain:
            if "localhost" not in domain:
                checks.append(("WARNING", "QR_CODE_DOMAIN missing port for HTTP"))
        else:
            checks.append(("OK", "QR_CODE_DOMAIN configured for HTTP"))

    # Check CORS
    print("")
    print("-" * 60)
    print("CORS Settings:")
    print(f"  BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")

    cors_origins = settings.BACKEND_CORS_ORIGINS
    expected_origin = f"{protocol}://{domain}"

    if expected_origin in cors_origins:
        checks.append(("OK", "CORS includes QR_CODE_DOMAIN"))
    else:
        checks.append(("WARNING", f"CORS may be missing: {expected_origin}"))

    # Check Security
    print("")
    print("-" * 60)
    print("Security Settings:")
    print(f"  SECRET_KEY: {'*' * 20}... (hidden)")
    print(f"  ALGORITHM:  {settings.ALGORITHM}")
    print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")

    if settings.SECRET_KEY == "your-secret-key-here-please-generate-a-new-one":
        checks.append(("ERROR", "SECRET_KEY is using default value - CHANGE IT!"))
    elif len(settings.SECRET_KEY) < 32:
        checks.append(("WARNING", "SECRET_KEY may be too short"))
    else:
        checks.append(("OK", "SECRET_KEY is set"))

    # Check Debug
    print("")
    print("-" * 60)
    print("Application Settings:")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  APP_NAME: {settings.APP_NAME}")
    print(f"  APP_VERSION: {settings.APP_VERSION}")

    if settings.DEBUG:
        checks.append(("WARNING", "DEBUG is True - should be False in production"))
    else:
        checks.append(("OK", "DEBUG is False"))

    # Summary
    print("")
    print("=" * 60)
    print("CHECK RESULTS:")
    print("=" * 60)

    errors = [c for c in checks if c[0] == "ERROR"]
    warnings = [c for c in checks if c[0] == "WARNING"]
    oks = [c for c in checks if c[0] == "OK"]

    for status, msg in checks:
        if status == "ERROR":
            print(f"  [ERROR]   {msg}")
        elif status == "WARNING":
            print(f"  [WARNING] {msg}")
        else:
            print(f"  [OK]      {msg}")

    print("")
    print("-" * 60)
    print(f"Summary: {len(oks)} OK, {len(warnings)} Warnings, {len(errors)} Errors")

    if errors:
        print("")
        print("ACTION REQUIRED: Fix errors before continuing!")
    elif warnings:
        print("")
        print("Review warnings to ensure configuration is correct.")
    else:
        print("")
        print("All checks passed!")

    print("=" * 60)

    # Show sample QR code URL
    print("")
    print("Sample QR Code URL that will be generated:")
    print(f"  {protocol}://{domain}/e/MBES-2024-001")
    print("")


if __name__ == "__main__":
    check_environment()
