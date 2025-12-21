@echo off
REM AID Sanity Test Runner for Windows
REM Runs all installation and sanity tests

echo ==========================================
echo AID Installation ^& Sanity Tests
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.9+
    exit /b 1
)

REM Check if pytest is available
python -m pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pytest...
    pip install pytest pytest-cov
)

REM Change to project root
cd /d "%~dp0\.."

echo.
echo [1/4] Running Installation Tests...
echo ------------------------------------------
python -m pytest testing/e2e/test_installation.py -v --tb=short -x

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation tests failed!
    echo Please fix the issues above before continuing.
    exit /b 1
)

echo.
echo [2/4] Running Memory System Sanity Tests...
echo ------------------------------------------
python -m pytest testing/e2e/test_memory_system_sanity.py -v --tb=short

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some memory system tests failed.
    echo Continuing with other tests...
)

echo.
echo [3/4] Running MCP Configuration Tests...
echo ------------------------------------------
python -m pytest testing/e2e/test_mcp_sanity.py -v --tb=short -m "not integration"

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some MCP configuration tests failed.
    echo Continuing with other tests...
)

echo.
echo [4/4] Running TypeScript Tests...
echo ------------------------------------------
call npm test -- --passWithNoTests --testPathPattern="__tests__"

echo.
echo ==========================================
echo Sanity Test Summary
echo ==========================================
echo.
echo All basic sanity tests completed.
echo.
echo To run full integration tests (requires network):
echo   pytest testing/e2e/ -v -m integration
echo.
echo To run with coverage:
echo   pytest testing/e2e/ -v --cov=memory-system --cov-report=html
echo.
