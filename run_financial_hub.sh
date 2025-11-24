#!/bin/bash
# Financial Hub Builder - Unix/Mac Bash Launcher
# This ensures the script runs from the correct directory

# Change to script directory
cd "$(dirname "$0")"

echo "================================================================================"
echo "Financial Hub Builder"
echo "================================================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if financial_docs exists
if [ ! -f "financial_docs/build_all.py" ]; then
    echo "ERROR: financial_docs/build_all.py not found"
    echo "Please run this script from the repository root directory"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Running Financial Hub Builder..."
echo ""

# Run the builder
python3 financial_docs/build_all.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "Build completed successfully!"
    echo "================================================================================"
    echo ""
    echo "To view your financial hub:"
    echo "  - Open: financial_docs/financial_hub.html"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo "Build failed with errors"
    echo "================================================================================"
    echo ""
fi

read -p "Press Enter to exit..."
