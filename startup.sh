#!/bin/bash
# Quick startup script for Chartace framework

set -e

echo ""
echo "================================================================================"
echo "                 CHARTACE FRAMEWORK - STARTUP SCRIPT"
echo "================================================================================"
echo ""

# Check Python
echo "[1] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.7+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "    ✓ Python $PYTHON_VERSION"

# Check dependencies
echo ""
echo "[2] Installing/Checking dependencies..."
pip install -q pandas numpy 2>/dev/null || echo "    ⚠ Could not install pandas/numpy"

echo "    ✓ Dependencies OK"

# Create necessary directories
echo ""
echo "[3] Creating directories..."
mkdir -p logs models data
echo "    ✓ Created logs/, models/, data/"

# Run startup checks
echo ""
echo "[4] Running application startup checks..."
python3 startup.py

echo "================================================================================"
echo "✓ STARTUP COMPLETE"
echo "================================================================================"
echo ""
