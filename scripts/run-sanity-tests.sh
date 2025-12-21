#!/bin/bash
# AID Sanity Test Runner for macOS/Linux
# Runs all installation and sanity tests

set -e

echo "=========================================="
echo "AID Installation & Sanity Tests"
echo "=========================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.9+"
    exit 1
fi

# Check if pytest is available
if ! python3 -m pytest --version &> /dev/null; then
    echo "Installing pytest..."
    pip3 install pytest pytest-cov
fi

# Change to project root
cd "$(dirname "$0")/.."

echo
echo "[1/4] Running Installation Tests..."
echo "------------------------------------------"
python3 -m pytest testing/e2e/test_installation.py -v --tb=short -x

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Installation tests failed!"
    echo "Please fix the issues above before continuing."
    exit 1
fi

echo
echo "[2/4] Running Memory System Sanity Tests..."
echo "------------------------------------------"
python3 -m pytest testing/e2e/test_memory_system_sanity.py -v --tb=short || true

echo
echo "[3/4] Running MCP Configuration Tests..."
echo "------------------------------------------"
python3 -m pytest testing/e2e/test_mcp_sanity.py -v --tb=short -m "not integration" || true

echo
echo "[4/4] Running TypeScript Tests..."
echo "------------------------------------------"
npm test -- --passWithNoTests --testPathPattern="__tests__" || true

echo
echo "=========================================="
echo "Sanity Test Summary"
echo "=========================================="
echo
echo "All basic sanity tests completed."
echo
echo "To run full integration tests (requires network):"
echo "  pytest testing/e2e/ -v -m integration"
echo
echo "To run with coverage:"
echo "  pytest testing/e2e/ -v --cov=memory-system --cov-report=html"
echo
