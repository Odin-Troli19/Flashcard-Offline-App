#!/bin/bash
# Enhanced Flashcard App - Installation Script

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   Enhanced Flashcard App - Installation              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ Python 3 not found!"
    echo "  Please install Python 3 from https://python.org"
    exit 1
fi

echo ""
echo "Installing required packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install Pillow
echo ""
echo "Installing Pillow for image support..."
pip3 install Pillow

if [ $? -eq 0 ]; then
    echo "✓ Pillow installed successfully!"
else
    echo "⚠ Pillow installation failed, but app will still work without images"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Installation complete!"
echo ""
echo "To run the app:"
echo "  python3 flashcard_app_improved.py"
echo ""
echo "For help, read:"
echo "  • README.md - Full documentation"
echo "  • QUICKSTART.txt - Quick reference"
echo "  • IMPROVEMENTS_SUMMARY.txt - What's new"
echo ""
echo "Happy studying! 📚✨"
