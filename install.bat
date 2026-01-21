@echo off
REM ============================================
REM AID - AI Development Methodology Installer
REM For Windows
REM Updated: 2025-12-31 - Cross-platform MCP config
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    AID Installation Script (Windows)
echo ========================================
echo.

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js found

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm not found!
    pause
    exit /b 1
)

echo [OK] npm found

REM Install npm dependencies
echo.
echo [STEP 1/8] Installing npm dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] npm install had issues, continuing...
)

REM Create .claude directories
echo.
echo [STEP 2/8] Setting up Claude commands and skills...
if not exist ".claude\commands" mkdir ".claude\commands"
if not exist ".claude\skills" mkdir ".claude\skills"
if not exist ".claude\references" mkdir ".claude\references"

REM Note: Commands are stored in .claude\commands\ (already in git)
REM Do NOT use skills\commands\ - that's not a valid Claude Code pattern
echo [OK] Commands installed

REM Copy skills to .claude/skills
echo Copying skills...
REM Core methodology skills
xcopy /E /I /Y "skills\aid-development" ".claude\skills\aid-development" >nul 2>nul
xcopy /E /I /Y "skills\aid-discovery" ".claude\skills\aid-discovery" >nul 2>nul
xcopy /E /I /Y "skills\aid-prd" ".claude\skills\aid-prd" >nul 2>nul
xcopy /E /I /Y "skills\aid-qa-ship" ".claude\skills\aid-qa-ship" >nul 2>nul
xcopy /E /I /Y "skills\aid-tech-spec" ".claude\skills\aid-tech-spec" >nul 2>nul
REM Design system skills
xcopy /E /I /Y "skills\atomic-design" ".claude\skills\atomic-design" >nul 2>nul
xcopy /E /I /Y "skills\atomic-page-builder" ".claude\skills\atomic-page-builder" >nul 2>nul
REM Development skills
xcopy /E /I /Y "skills\aid-impl-plan" ".claude\skills\aid-impl-plan" >nul 2>nul
xcopy /E /I /Y "skills\code-review" ".claude\skills\code-review" >nul 2>nul
xcopy /E /I /Y "skills\context-tracking" ".claude\skills\context-tracking" >nul 2>nul
xcopy /E /I /Y "skills\learning-mode" ".claude\skills\learning-mode" >nul 2>nul
xcopy /E /I /Y "skills\phase-enforcement" ".claude\skills\phase-enforcement" >nul 2>nul
xcopy /E /I /Y "skills\pre-prd-research" ".claude\skills\pre-prd-research" >nul 2>nul
xcopy /E /I /Y "skills\system-architect" ".claude\skills\system-architect" >nul 2>nul
xcopy /E /I /Y "skills\test-driven" ".claude\skills\test-driven" >nul 2>nul
REM Role-based skills
xcopy /E /I /Y "skills\role-developer" ".claude\skills\role-developer" >nul 2>nul
xcopy /E /I /Y "skills\role-product-manager" ".claude\skills\role-product-manager" >nul 2>nul
xcopy /E /I /Y "skills\role-qa-engineer" ".claude\skills\role-qa-engineer" >nul 2>nul
xcopy /E /I /Y "skills\role-tech-lead" ".claude\skills\role-tech-lead" >nul 2>nul
REM Optional skills
xcopy /E /I /Y "skills\nano-banana-visual" ".claude\skills\nano-banana-visual" >nul 2>nul
xcopy /E /I /Y "skills\figma-design-review" ".claude\skills\figma-design-review" >nul 2>nul
REM Foundational skills
xcopy /E /I /Y "skills\why-driven-decision" ".claude\skills\why-driven-decision" >nul 2>nul
xcopy /E /I /Y "skills\reflection" ".claude\skills\reflection" >nul 2>nul
xcopy /E /I /Y "skills\aid-test-agent" ".claude\skills\aid-test-agent" >nul 2>nul
echo [OK] Skills installed (24 skills)

REM Create .aid directory
echo.
echo [STEP 3/8] Creating project state directory...
if not exist ".aid" mkdir ".aid"

REM Create state.json if it doesn't exist
echo [STEP 4/8] Creating state files...
if not exist ".aid\state.json" (
    (
    echo {
    echo   "$schema": "aid-state-v1",
    echo   "version": "1.0",
    echo   "initialized_at": "%DATE% %TIME%",
    echo   "last_updated": "%DATE% %TIME%",
    echo   "current_phase": 0,
    echo   "phase_name": "Discovery",
    echo   "phase_approved": false,
    echo   "current_session": {
    echo     "active": false,
    echo     "role": null,
    echo     "phase": null,
    echo     "started_at": null,
    echo     "revision_count": 0
    echo   },
    echo   "last_session": {
    echo     "role": null,
    echo     "phase": null,
    echo     "completed_at": null
    echo   },
    echo   "statistics": {
    echo     "total_sessions": 0,
    echo     "total_feedback_collected": 0,
    echo     "pending_feedback_count": 0,
    echo     "last_improvement_run": null,
    echo     "sessions_since_last_improvement": 0
    echo   },
    echo   "notifications": {
    echo     "improvement_suggested": false,
    echo     "reason": null
    echo   }
    echo }
    ) > ".aid\state.json"
    echo [OK] State file created
) else (
    echo [OK] State file already exists
)

REM Create context.json if it doesn't exist
if not exist ".aid\context.json" (
    (
    echo {
    echo   "$schema": "aid-context-v1",
    echo   "version": "1.0",
    echo   "last_updated": "%DATE% %TIME%",
    echo   "current_task": null,
    echo   "current_step": null,
    echo   "progress": {
    echo     "steps_completed": [],
    echo     "steps_pending": []
    echo   },
    echo   "session_notes": [],
    echo   "blockers": []
    echo }
    ) > ".aid\context.json"
    echo [OK] Context file created
) else (
    echo [OK] Context file already exists
)


REM Create global ~/.aid directory for learning system
echo.
echo [STEP 5/8] Setting up global AID learning system...
set "AID_HOME=%USERPROFILE%\.aid"
if not exist "%AID_HOME%" mkdir "%AID_HOME%"
if not exist "%AID_HOME%\feedback" mkdir "%AID_HOME%\feedback"
if not exist "%AID_HOME%\feedback\pending" mkdir "%AID_HOME%\feedback\pending"
if not exist "%AID_HOME%\feedback\processed" mkdir "%AID_HOME%\feedback\processed"
if not exist "%AID_HOME%\metrics" mkdir "%AID_HOME%\metrics"
if not exist "%AID_HOME%\logs" mkdir "%AID_HOME%\logs"
if not exist "%AID_HOME%\skills" mkdir "%AID_HOME%\skills"

REM Copy templates to global config
echo [OK] Global learning system initialized at %AID_HOME%

REM Create .mcp.json from Windows template (no inline defaults)
echo.
echo [STEP 6/8] Creating MCP configuration (Windows)...
if not exist ".mcp.json" (
    if exist ".mcp.json.windows" (
        copy ".mcp.json.windows" ".mcp.json" >nul
        echo [OK] MCP configuration created from Windows template
        echo.
        echo   NOTE: Edit .mcp.json to add your API tokens:
        echo     - ATLASSIAN_API_TOKEN (for Jira/Confluence^)
        echo     - FIGMA_API_KEY (for Figma^)
        echo     - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub^)
    ) else (
        echo [ERROR] .mcp.json.windows template not found!
        echo.
        echo   The Windows MCP template is required for installation.
        echo   Please ensure .mcp.json.windows exists in the AID folder.
        echo.
        echo   You can create it manually or download from the AID repository.
    )
) else (
    echo [OK] MCP configuration already exists
)

REM Create .env if not exists
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env from template
    )
) else (
    echo [OK] .env already exists
)

REM Verify MCP configuration
echo.
echo [STEP 7/8] Verifying MCP configuration...
if exist ".mcp.json" (
    echo [OK] MCP configuration found

    findstr /C:"YOUR_" ".mcp.json" >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo [WARNING] MCP tokens not configured yet
        echo   Edit .mcp.json and replace YOUR_* placeholders with real tokens
    )
) else (
    echo [WARNING] No .mcp.json found - MCP servers won't work
    echo   Run: copy .mcp.json.windows .mcp.json
)

REM Step 8: Setup Storybook preview server
echo.
echo [STEP 8/8] Setting up Storybook preview server...
if not exist "storybook-preview" (
    echo [WARNING] storybook-preview folder not found, skipping
    goto :after_storybook
)

echo Installing Storybook dependencies (this may take a minute)...
echo Please wait...
cd storybook-preview
call npm install >nul 2>&1
echo [OK] Storybook dependencies installed

REM Create atomic design component directories
if not exist "src\components\atoms" mkdir "src\components\atoms"
if not exist "src\components\molecules" mkdir "src\components\molecules"
if not exist "src\components\organisms" mkdir "src\components\organisms"
if not exist "src\components\templates" mkdir "src\components\templates"
if not exist "src\components\pages" mkdir "src\components\pages"

cd ..
echo [OK] Storybook ready - use /storybook command to preview components

:after_storybook

REM Pre-install MCP servers for faster startup
echo.
echo [BONUS] Pre-caching MCP server packages...
echo   This speeds up first Claude Code startup.
echo.
echo   Caching: @modelcontextprotocol/server-filesystem...
call npm cache add @modelcontextprotocol/server-filesystem >nul 2>nul
echo   Caching: chrome-devtools-mcp...
call npm cache add chrome-devtools-mcp >nul 2>nul
echo   Caching: @aashari/mcp-server-atlassian-jira...
call npm cache add @aashari/mcp-server-atlassian-jira >nul 2>nul
echo   Caching: @aashari/mcp-server-atlassian-confluence...
call npm cache add @aashari/mcp-server-atlassian-confluence >nul 2>nul
echo   Caching: figma-developer-mcp...
call npm cache add figma-developer-mcp >nul 2>nul
echo   Caching: @modelcontextprotocol/server-github...
call npm cache add @modelcontextprotocol/server-github >nul 2>nul
echo [OK] MCP server packages cached

:finish
echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo MCP servers configured in .mcp.json:
if exist ".mcp.json" (
    node -e "const f=require('./.mcp.json'); Object.keys(f.mcpServers||{}).forEach(s=>console.log('  - '+s))" 2>nul
)
echo.
echo Next steps:
echo.
echo 1. Edit .mcp.json with your API tokens:
echo    - ATLASSIAN_API_TOKEN (for Jira/Confluence)
echo    - FIGMA_API_KEY (for Figma)
echo    - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub)
echo.
echo 2. Start Claude Code FROM THIS FOLDER:
echo    cd "%CD%"
echo    claude
echo.
echo 3. Inside Claude Code, verify MCP with: /mcp
echo.
echo 4. Run /aid-start to begin working!
echo.
echo 5. (OPTIONAL^) Preview Figma components in Storybook:
echo    - Extract component from Figma plugin
echo    - Tell Claude: "Add ComponentName to Storybook"
echo    - Or use: /storybook add .\path\to\Component
echo    - View at http://localhost:6006
echo.
echo NOTE: MCP servers are PROJECT-SCOPED.
echo       They only work when running Claude from this folder.
echo.
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
