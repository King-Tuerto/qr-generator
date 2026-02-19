# QR Code Generator - Agent Instructions

## What This Is
A QR code generator with two interfaces:
- **Web tool**: qr-generator.html (hosted on GitHub Pages)
- **Python tool**: tools/generate_qr.py (used from Claude Code)

## WAT Framework
- `workflows/` - SOPs for common tasks
- `tools/` - Python scripts for execution
- `archive/` - Generated QR codes (PNG + PDF), pushed to GitHub

## Common Tasks
- **Generating a QR code**: Read `workflows/generate_qr_code.md`, then run `tools/generate_qr.py`
- After generating, always commit and push `archive/` to GitHub

## Key Constraint
Paul is non-technical. Everything must just work. The tool auto-installs missing dependencies.
