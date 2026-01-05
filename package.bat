@echo off
REM ============================================
REM AID - Package for Distribution
REM Creates a clean copy ready for sharing
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    AID Distribution Packager
echo ========================================
echo.

REM Get source path (where this script is located)
set "SOURCE_PATH=%~dp0"
set "SOURCE_PATH=%SOURCE_PATH:~0,-1%"

echo Source: %SOURCE_PATH%
echo.

REM Get destination path
if "%~1"=="" (
    set /p "DEST_PATH=Enter destination folder: "
) else (
    set "DEST_PATH=%~1"
)

REM Remove trailing backslash if present
if "%DEST_PATH:~-1%"=="\" set "DEST_PATH=%DEST_PATH:~0,-1%"

REM Create destination folder name with timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set "DATETIME=%%I"
set "TIMESTAMP=%DATETIME:~0,8%"
set "PACKAGE_NAME=aid-package-%TIMESTAMP%"
set "FULL_DEST=%DEST_PATH%\%PACKAGE_NAME%"

echo.
echo Destination: %FULL_DEST%
echo.

REM Check if destination already exists
if exist "%FULL_DEST%" (
    echo [ERROR] Destination already exists: %FULL_DEST%
    echo         Please remove it or choose a different location.
    pause
    exit /b 1
)

REM Create destination directory
mkdir "%FULL_DEST%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Could not create destination directory
    pause
    exit /b 1
)

echo [STEP 1/4] Copying core files...
echo.

REM Copy using robocopy with exclusions
REM /E = include subdirectories (even empty ones)
REM /XD = exclude directories
REM /XF = exclude files
robocopy "%SOURCE_PATH%" "%FULL_DEST%" /E ^
    /XD node_modules .aid __pycache__ .git .vscode .idea ^
    /XF .env .mcp.json *.pyc *.egg-info .DS_Store Thumbs.db ^
    /NFL /NDL /NJH /NJS /NC /NS

echo.
echo [STEP 2/4] Cleaning up Python cache...

REM Remove any __pycache__ that might have slipped through
for /d /r "%FULL_DEST%" %%d in (__pycache__) do (
    if exist "%%d" rd /s /q "%%d" 2>nul
)

REM Remove .egg-info directories
for /d /r "%FULL_DEST%" %%d in (*.egg-info) do (
    if exist "%%d" rd /s /q "%%d" 2>nul
)

echo [OK] Python cache cleaned

echo.
echo [STEP 3/4] Verifying essential files...

set "MISSING=0"

REM Check for essential files
if not exist "%FULL_DEST%\install.bat" (
    echo [MISSING] install.bat
    set "MISSING=1"
)
if not exist "%FULL_DEST%\install.sh" (
    echo [MISSING] install.sh
    set "MISSING=1"
)
if not exist "%FULL_DEST%\.mcp.json.windows" (
    echo [MISSING] .mcp.json.windows
    set "MISSING=1"
)
if not exist "%FULL_DEST%\.mcp.json.mac" (
    echo [MISSING] .mcp.json.mac
    set "MISSING=1"
)
if not exist "%FULL_DEST%\.env.example" (
    echo [MISSING] .env.example
    set "MISSING=1"
)
if not exist "%FULL_DEST%\CLAUDE.md" (
    echo [MISSING] CLAUDE.md
    set "MISSING=1"
)
if not exist "%FULL_DEST%\memory-system\pyproject.toml" (
    echo [MISSING] memory-system\pyproject.toml
    set "MISSING=1"
)
if not exist "%FULL_DEST%\memory-system\memory_system\__init__.py" (
    echo [MISSING] memory-system\memory_system\__init__.py
    set "MISSING=1"
)
if not exist "%FULL_DEST%\skills" (
    echo [MISSING] skills folder
    set "MISSING=1"
)

if "%MISSING%"=="0" (
    echo [OK] All essential files present
) else (
    echo.
    echo [WARNING] Some files are missing - package may be incomplete
)

echo.
echo [STEP 4/4] Calculating package size...

REM Count files and size
set "FILE_COUNT=0"
for /r "%FULL_DEST%" %%f in (*) do set /a FILE_COUNT+=1

echo.
echo ========================================
echo    Package Created Successfully!
echo ========================================
echo.
echo Location: %FULL_DEST%
echo Files:    %FILE_COUNT%
echo.
echo Package contents:
echo   - install.bat / install.sh (installers)
echo   - link-project.bat / link-project.sh (project linkers)
echo   - .mcp.json.windows / .mcp.json.mac (MCP templates)
echo   - .env.example (environment template)
echo   - skills/ (20 AID skills)
echo   - memory-system/ (learning system)
echo   - CLAUDE.md (project instructions)
echo.
echo ----------------------------------------
echo.
echo To use on another machine:
echo.
echo   1. Copy %PACKAGE_NAME% folder to target machine
echo   2. Open terminal in that folder
echo   3. Run: install.bat (Windows) or ./install.sh (Mac)
echo   4. Edit .mcp.json with your API tokens
echo   5. Run: claude
echo   6. Type: /aid-start
echo.
echo ========================================
echo.
pause
