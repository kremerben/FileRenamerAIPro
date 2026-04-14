#!/bin/bash

# Build script for File Renamer AI Pro on macOS
# This script uses PyInstaller to package the application into a standalone .app bundle.

# 1. Ensure dependencies are installed
echo "Installing dependencies..."
pip install pyinstaller PyQt6 pymupdf Pillow

# 2. Run PyInstaller
# --windowed: Creates a .app bundle and hides the terminal console when the app starts.
# --noconfirm: Replaces the output directory without asking.
# --clean: Cleans PyInstaller cache before building.
# --name: Specifies the name of the app bundle.
# --target-arch: (Optional) Set to 'universal2' to build for both Intel and Apple Silicon.
#                Requires a universal Python and all dependencies must have universal2 or 
#                separate x86_64/arm64 wheels available.
#                Alternatively, build on an Intel Mac to create an Intel-only bundle.
ARCH=$(uname -m)
echo "Building for $ARCH architecture..."
pyinstaller --windowed \
            --noconfirm \
            --clean \
            --name "FileRenamerAIPro" \
            main.py

echo "-------------------------------------------------------"
echo "Build complete! You can find the app in the 'dist' folder."
echo "To share it, zip 'dist/FileRenamerAIPro.app' and send it to other Macs."
echo "Note: If you encounter Gatekeeper issues on other Macs, tell the user to"
echo "Right-click -> Open, or go to System Settings -> Privacy & Security."
echo "-------------------------------------------------------"
