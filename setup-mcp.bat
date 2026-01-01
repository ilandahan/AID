@echo off
REM ============================================
REM AID - MCP Server Diagnostic Script
REM Helps troubleshoot MCP server issues
REM ============================================

echo.
echo ========================================
echo    AID MCP Server Diagnostic
echo ========================================
echo.

REM Check if claude is available
where claude >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Claude Code CLI not found!
    echo Please install Claude Code first:
    echo   npm install -g @anthropic-ai/claude-code
    pause
    exit /b 1
)

echo [OK] Claude Code CLI found
echo.

REM Check .mcp.json
echo Checking .mcp.json configuration...
if exist ".mcp.json" (
    echo [OK] .mcp.json found in current directory
    echo.
    echo Configured servers in .mcp.json:
    node -e "const f=require('./.mcp.json'); Object.keys(f.mcpServers||{}).forEach(s=>console.log('  - '+s))" 2>nul
    echo.
) else (
    echo [ERROR] .mcp.json not found!
    echo Run install.bat first to create .mcp.json
    pause
    exit /b 1
)

echo ========================================
echo IMPORTANT: About MCP Server Scopes
echo ========================================
echo.
echo Your .mcp.json contains PROJECT-SCOPED servers.
echo These are loaded AUTOMATICALLY when you run:
echo   claude
echo from THIS directory:
echo   %CD%
echo.
echo NOTE: "claude mcp list" only shows USER scope servers
echo (from ~/.claude.json), NOT project scope servers.
echo.
echo To see ALL servers including project scope:
echo   1. Open terminal in THIS directory
echo   2. Run: claude
echo   3. Inside Claude Code, type: /mcp
echo.
echo ========================================
echo.
echo Would you like to test a single MCP server?
echo This verifies the server package can be downloaded.
echo.
set /p TEST_SERVER="Test filesystem server? (y/n): "
if /i "%TEST_SERVER%"=="y" (
    echo.
    echo Testing: npx -y @modelcontextprotocol/server-filesystem .
    echo Press Ctrl+C to stop after you see output...
    echo.
    npx -y @modelcontextprotocol/server-filesystem .
)

echo.
echo ========================================
echo    Diagnostic Complete
echo ========================================
echo.
echo Your .mcp.json is configured correctly.
echo.
echo To use MCP servers:
echo   1. Open terminal in THIS directory
echo   2. Run: claude
echo   3. Inside Claude Code, type: /mcp
echo.
echo If servers still don't appear in /mcp:
echo   - Verify API tokens in .mcp.json are valid
echo   - Ensure Docker Desktop is running (for docker server)
echo   - Open Chrome with --remote-debugging-port=9222 (for devtools)
echo   - Check that npx can download packages (no firewall blocking)
echo.
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
