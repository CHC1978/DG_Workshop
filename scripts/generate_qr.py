#!/usr/bin/env python
"""
Custom QR Code Generator
Generate QR codes for any URL

Usage:
    python generate_qr.py <url> [output_file]

Examples:
    python generate_qr.py https://neptus-station.boga-ulmer.ts.net:8443/login
    python generate_qr.py https://neptus-station.boga-ulmer.ts.net:8443/login login_qr.png
    python generate_qr.py --interactive
"""
import sys
import os

# Add backend to path for using existing qrcode library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
except ImportError:
    print("Error: qrcode library not found.")
    print("Install with: pip install qrcode[pil]")
    sys.exit(1)

from datetime import datetime

# Default settings
DEFAULT_DOMAIN = "neptus-station.boga-ulmer.ts.net:8443"
DEFAULT_PROTOCOL = "https"

# Common URLs
COMMON_URLS = {
    "1": ("Login Page", "/login"),
    "2": ("Dashboard", "/dashboard"),
    "3": ("Equipment List", "/equipment"),
    "4": ("API Docs", "/api/docs"),
    "5": ("Health Check", "/api/health"),
}


def generate_qr_code(url: str, output_path: str = None, box_size: int = 10, border: int = 4, error_correction=ERROR_CORRECT_M):
    """
    Generate QR code for given URL

    Args:
        url: The URL to encode
        output_path: Output file path (optional, will auto-generate if not provided)
        box_size: Size of each box in the QR code
        border: Border size around the QR code
        error_correction: Error correction level (L, M, Q, H)

    Returns:
        Path to the generated QR code image
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")

    # Determine output path
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"qr_{timestamp}.png"

    # Save image
    img.save(output_path)

    return output_path


def interactive_mode():
    """Interactive QR code generation"""
    print("=" * 60)
    print("QR Code Generator - Interactive Mode")
    print("=" * 60)
    print(f"Default domain: {DEFAULT_PROTOCOL}://{DEFAULT_DOMAIN}")
    print("")

    while True:
        print("-" * 60)
        print("Options:")
        print("  [1-5] Generate QR for common pages")
        for key, (name, path) in COMMON_URLS.items():
            print(f"    {key}. {name} ({path})")
        print("  [C]   Custom URL")
        print("  [F]   Full custom URL (enter complete URL)")
        print("  [Q]   Quit")
        print("")

        choice = input("Select option: ").strip().upper()

        if choice == "Q":
            print("Goodbye!")
            break
        elif choice in COMMON_URLS:
            name, path = COMMON_URLS[choice]
            url = f"{DEFAULT_PROTOCOL}://{DEFAULT_DOMAIN}{path}"
            output_name = input(f"Output filename (default: {name.lower().replace(' ', '_')}_qr.png): ").strip()
            if not output_name:
                output_name = f"{name.lower().replace(' ', '_')}_qr.png"

            output_path = generate_qr_code(url, output_name)
            print(f"\nGenerated QR code for: {url}")
            print(f"Saved to: {output_path}")
            print("")

        elif choice == "C":
            path = input("Enter path (e.g., /login, /equipment/1): ").strip()
            if not path.startswith("/"):
                path = "/" + path
            url = f"{DEFAULT_PROTOCOL}://{DEFAULT_DOMAIN}{path}"

            output_name = input("Output filename (press Enter for auto): ").strip()
            output_path = generate_qr_code(url, output_name if output_name else None)
            print(f"\nGenerated QR code for: {url}")
            print(f"Saved to: {output_path}")
            print("")

        elif choice == "F":
            url = input("Enter full URL: ").strip()
            if not url:
                print("Error: URL cannot be empty")
                continue

            output_name = input("Output filename (press Enter for auto): ").strip()
            output_path = generate_qr_code(url, output_name if output_name else None)
            print(f"\nGenerated QR code for: {url}")
            print(f"Saved to: {output_path}")
            print("")

        else:
            print("Invalid option. Please try again.")


def main():
    """Main entry point"""
    args = sys.argv[1:]

    # Interactive mode
    if not args or args[0] == "--interactive" or args[0] == "-i":
        interactive_mode()
        return

    # Help
    if args[0] in ("--help", "-h"):
        print(__doc__)
        print("\nCommon URLs:")
        for key, (name, path) in COMMON_URLS.items():
            full_url = f"{DEFAULT_PROTOCOL}://{DEFAULT_DOMAIN}{path}"
            print(f"  {name}: {full_url}")
        return

    # Command line mode
    url = args[0]
    output_path = args[1] if len(args) > 1 else None

    # If URL is just a path, prepend domain
    if url.startswith("/"):
        url = f"{DEFAULT_PROTOCOL}://{DEFAULT_DOMAIN}{url}"
    elif not url.startswith("http"):
        url = f"{DEFAULT_PROTOCOL}://{url}"

    print(f"Generating QR code for: {url}")
    output_path = generate_qr_code(url, output_path)
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
