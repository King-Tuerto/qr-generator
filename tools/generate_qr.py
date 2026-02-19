#!/usr/bin/env python3
"""
generate_qr.py - Generate QR codes and save as PNG + PDF to the archive.

Supports URLs, plain text, email addresses, phone numbers, and WiFi credentials.
Part of the WAT framework (tools layer).

Usage:
    python tools/generate_qr.py --content "https://example.com" --label "My Website"
    python tools/generate_qr.py --content "paul@example.com"
    python tools/generate_qr.py --content "+1-555-123-4567" --label "Office Phone"
    python tools/generate_qr.py --content "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;" --label "Home WiFi"
    python tools/generate_qr.py --content "Hello World" --type text
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import date


# ---------------------------------------------------------------------------
# Dependency management — auto-install if missing
# ---------------------------------------------------------------------------

def ensure_dependencies():
    """Install missing dependencies so Paul never has to touch pip."""
    missing = []
    try:
        import qrcode  # noqa: F401
    except ImportError:
        missing.append("qrcode[pil]")
    try:
        from fpdf import FPDF  # noqa: F401
    except ImportError:
        missing.append("fpdf2")
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        missing.append("Pillow")

    if missing:
        print(f"Installing missing libraries: {', '.join(missing)}...")
        for pkg in missing:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        print("Done.\n")


# ---------------------------------------------------------------------------
# Auto-detect content type
# ---------------------------------------------------------------------------

def detect_type(content: str) -> str:
    """Auto-detect the QR content type from the string."""
    c = content.strip()
    if c.upper().startswith("WIFI:"):
        return "wifi"
    if re.match(r'^https?://', c, re.IGNORECASE):
        return "url"
    if re.match(r'^www\.', c, re.IGNORECASE):
        return "url"
    if re.match(r'^mailto:', c, re.IGNORECASE):
        return "email"
    if re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', c):
        return "email"
    if re.match(r'^tel:', c, re.IGNORECASE):
        return "phone"
    if re.match(r'^\+?[\d\s\-\(\)]{7,}$', c):
        return "phone"
    return "text"


# ---------------------------------------------------------------------------
# Format content for QR encoding
# ---------------------------------------------------------------------------

def format_content(content: str, qr_type: str) -> str:
    """Add standard prefixes (mailto:, tel:, https://) as needed."""
    c = content.strip()
    if qr_type == "url":
        if not re.match(r'^https?://', c, re.IGNORECASE):
            c = "https://" + c
    elif qr_type == "email":
        if not c.lower().startswith("mailto:"):
            c = "mailto:" + c
    elif qr_type == "phone":
        if not c.lower().startswith("tel:"):
            c = "tel:" + c
    return c


# ---------------------------------------------------------------------------
# Generate QR code image
# ---------------------------------------------------------------------------

def generate_qr_image(data: str):
    """Generate a QR code as a PIL Image."""
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


# ---------------------------------------------------------------------------
# Filename helpers
# ---------------------------------------------------------------------------

def make_filename(label: str) -> str:
    """Create a safe filename from the label + today's date."""
    safe = re.sub(r'[^\w\s\-]', '', label)[:50].strip()
    safe = re.sub(r'\s+', '-', safe).lower()
    if not safe:
        safe = "qr-code"
    today = date.today().isoformat()
    return f"{safe}_{today}"


def resolve_paths(archive_dir: str, base_name: str):
    """Return (png_path, pdf_path), handling collisions."""
    png_path = os.path.join(archive_dir, f"{base_name}.png")
    pdf_path = os.path.join(archive_dir, f"{base_name}.pdf")

    counter = 2
    while os.path.exists(png_path) or os.path.exists(pdf_path):
        png_path = os.path.join(archive_dir, f"{base_name}-{counter}.png")
        pdf_path = os.path.join(archive_dir, f"{base_name}-{counter}.pdf")
        counter += 1

    return png_path, pdf_path


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def create_pdf(qr_image, label: str, content: str, qr_type: str, output_path: str):
    """Create a PDF with the QR code, label, encoded content, and date."""
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    pdf = FPDF(orientation="P", unit="mm", format="letter")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, text=label, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)

    # Type badge
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, text=f"Type: {qr_type.upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)

    # Save QR image to temp file for embedding
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
            qr_image.save(tmp_path)

        # Center the QR code — 100mm wide (~4 inches, large and scannable)
        page_width = pdf.w - pdf.l_margin - pdf.r_margin
        qr_size = 100
        x_offset = (page_width - qr_size) / 2 + pdf.l_margin
        pdf.image(tmp_path, x=x_offset, y=pdf.get_y(), w=qr_size, h=qr_size)
        pdf.ln(qr_size + 10)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Encoded content
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, text=f"Encoded: {content}", align="C")
    pdf.ln(5)

    # Date
    pdf.set_font("Helvetica", "I", 10)
    today = date.today().strftime("%B %d, %Y")
    pdf.cell(0, 8, text=f"Created: {today}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.output(output_path)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a QR code and save as PNG + PDF to the archive."
    )
    parser.add_argument(
        "--content", required=True,
        help="The data to encode (URL, text, email, phone, WiFi string, etc.)"
    )
    parser.add_argument(
        "--label", default=None,
        help="Human-readable label for the PDF title and filename. Defaults to the content."
    )
    parser.add_argument(
        "--type", default=None, dest="qr_type",
        choices=["url", "text", "email", "phone", "wifi", "other"],
        help="Content type. Auto-detected if omitted."
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ensure_dependencies()

    args = parse_args()

    # Resolve type and label
    qr_type = args.qr_type or detect_type(args.content)
    label = args.label or args.content

    # Format content for QR encoding
    encoded_content = format_content(args.content, qr_type)

    # Generate QR image
    qr_image = generate_qr_image(encoded_content)

    # Set up archive directory
    site_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    archive_dir = os.path.join(site_root, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    # Build output paths (with collision handling)
    base_name = make_filename(label)
    png_path, pdf_path = resolve_paths(archive_dir, base_name)

    # Save PNG
    qr_image.save(png_path)

    # Save PDF
    create_pdf(qr_image, label, encoded_content, qr_type, pdf_path)

    # Summary
    print(f"\n{'='*50}")
    print(f"QR CODE GENERATED!")
    print(f"{'='*50}")
    print(f"  Label:   {label}")
    print(f"  Type:    {qr_type}")
    print(f"  Content: {encoded_content}")
    print(f"  PNG:     {png_path}")
    print(f"  PDF:     {pdf_path}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
