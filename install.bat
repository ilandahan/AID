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
echo [STEP 1/10] Installing npm dependencies...
REM npm ci: install exactly what package-lock.json pins (no silent upgrades)
call npm ci
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] npm ci had issues, continuing...
)

REM Create .claude directories
echo.
echo [STEP 2/10] Verifying Claude commands and skills...
REM Skills, commands, agents, rules, references and hooks all ship in git under
REM .claude\. There is NO copy step. This block used to run 25 xcopy lines against a
REM root skills\ directory that v2.1 removed, with output suppressed, so every copy
REM silently did nothing while reporting "Skills installed (24 skills)".
set "AID_MISSING=0"
for %%D in (commands skills agents rules references hooks) do (
    if exist ".claude\%%D" (
        echo [OK] .claude\%%D present
    ) else (
        echo [WARN] .claude\%%D is MISSING - restore it before using AID
        set "AID_MISSING=1"
    )
)
if "!AID_MISSING!"=="0" (
    echo [OK] AID content verified
) else (
    echo [WARN] Installation incomplete - see the warnings above
)

REM Create .aid directory
echo.
echo [STEP 3/10] Creating project state directory...
if not exist ".aid" mkdir ".aid"

REM .aid\state.json is NOT written here (T16-64, E3): hooks\aid_session.py is its only
REM writer. /aid-start runs `aid_session.py init`, which the user confirms.
echo [STEP 4/10] Creating state files...
if exist ".aid\state.json" (
    echo [OK] State file already exists
) else (
    echo [INFO] State file: created by /aid-start - aid_session.py init - not by the installer
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
echo [STEP 5/10] Setting up global AID learning system...
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
echo [STEP 6/10] Creating MCP configuration (Windows)...
if not exist ".mcp.json" (
    if exist ".mcp.json.windows" (
        copy ".mcp.json.windows" ".mcp.json" >nul
        echo [OK] MCP configuration created from Windows template
        echo.
        echo   NOTE: .mcp.json reads tokens from environment variables. Do NOT paste
        echo   tokens into it. Set them from Windows Credential Manager - see INSTALLATION.md:
        echo     - ATLASSIAN_SITE_NAME - subdomain only, ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN for Jira/Confluence
        echo     - GITHUB_PERSONAL_ACCESS_TOKEN for GitHub
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

REM No .env is created: tokens never go into a plaintext file.
REM Preference order: SSO/OAuth, then OS keystore, then environment variable.
echo [INFO] Tokens: store them in Windows Credential Manager, not in a .env file.
echo   See INSTALLATION.md, section "MCP Integrations Setup" - OS keystore table.

REM Verify MCP configuration
echo.
echo [STEP 7/10] Verifying MCP configuration...
if exist ".mcp.json" (
    echo [OK] MCP configuration found

    findstr /C:"YOUR_" ".mcp.json" >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo [WARNING] .mcp.json is an old template with inline token placeholders
        echo   Run: copy .mcp.json.windows .mcp.json  - it reads tokens from environment variables
    )
) else (
    echo [WARNING] No .mcp.json found - MCP servers won't work
    echo   Run: copy .mcp.json.windows .mcp.json
)

REM Step 8: Setup Storybook preview server
echo.
echo [STEP 8/10] Setting up Storybook preview server...
if not exist "storybook-preview" (
    echo [WARNING] storybook-preview folder not found, skipping
    goto :after_storybook
)

echo Installing Storybook dependencies (this may take a minute)...
echo Please wait...
cd storybook-preview
call npm ci >nul 2>&1
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

REM Step 9: Setup Cucumber BDD
echo.
echo ===============================================================
echo [STEP 9/10] Setting up Cucumber BDD...
echo ===============================================================

REM Create Cucumber directory structure
echo   Creating Cucumber directory structure...
if not exist "features\step-definitions" mkdir "features\step-definitions"
if not exist "features\support" mkdir "features\support"
if not exist "reports" mkdir "reports"
echo [OK] Cucumber directories created
echo     features\
echo       step-definitions\
echo       support\
echo     reports\

REM Copy Cucumber configuration
echo   Setting up Cucumber configuration...
if not exist "cucumber.js" (
    if exist "cucumber.js.template" (
        copy "cucumber.js.template" "cucumber.js" >nul
        echo [OK] Cucumber configuration created from template
    ) else (
        echo [WARNING] cucumber.js.template not found - creating minimal config
        (
        echo module.exports = {
        echo   default: {
        echo     require: ['features/step-definitions/**/*.ts', 'features/support/**/*.ts'],
        echo     requireModule: ['ts-node/register'],
        echo     format: ['progress-bar', 'html:reports/cucumber-report.html'],
        echo     publishQuiet: true
        echo   }
        echo };
        ) > "cucumber.js"
        echo [OK] Minimal Cucumber configuration created
    )
) else (
    echo [OK] Cucumber configuration already exists
)

REM Create World template
echo   Creating Cucumber World template...
if not exist "features\support\world.ts" (
    (
    echo // Cucumber World - Shared State Between Steps
    echo // Run install.sh on Mac/Linux for the full template
    echo import { setWorldConstructor, World, IWorldOptions } from '@cucumber/cucumber';
    echo.
    echo export interface ICustomWorld {
    echo   // Add your shared properties here
    echo }
    echo.
    echo export class CustomWorld extends World implements ICustomWorld {
    echo   constructor^(options: IWorldOptions^) {
    echo     super^(options^);
    echo   }
    echo }
    echo.
    echo setWorldConstructor^(CustomWorld^);
    ) > "features\support\world.ts"
    echo [OK] World template created
) else (
    echo [OK] World template already exists
)

echo [OK] Cucumber BDD setup complete
echo     Run "npm run cucumber" to execute feature files

echo.
echo ===============================================================
echo [STEP 10/10] breather (optional: session break offers)
echo ===============================================================
REM T11: OPT-IN. It installs into %USERPROFILE%\.claude for every project, and its session-start
REM instructions tell Claude to fetch today's calendar events through any connected calendar
REM connector. It runs only after an explicit yes, or with the /breather argument.
echo breather installs into %USERPROFILE%\.claude for EVERY project (hooks + status line).
echo At session start it tells Claude to fetch today's calendar events through any connected
echo calendar connector (Google Calendar / Gmail, Microsoft 365 / Outlook) and record the
echo meeting times locally. See integrations\breather\README.md.
set "BREATHER_ANSWER=N"
echo %* | findstr /I /C:"/breather" >nul && set "BREATHER_ANSWER=Y"
if /I not "%BREATHER_ANSWER%"=="Y" set /p "BREATHER_ANSWER=Install breather? [y/N] "
if /I "%BREATHER_ANSWER%"=="Y" goto :breather_install
if /I "%BREATHER_ANSWER%"=="YES" goto :breather_install
echo [SKIP] breather not installed. Install later with /breather-start, or: node integrations\breather\install.mjs
goto :breather_done
:breather_install
call node integrations\breather\install.mjs
if %errorlevel% equ 0 (
    echo [OK] breather installed to %USERPROFILE%\.claude - all projects, active after Claude Code restart
) else (
    echo [WARNING] breather install failed - run manually: node integrations\breather\install.mjs
)
:breather_done

REM Pre-install MCP servers for faster startup
echo.
echo [BONUS] Pre-caching MCP server packages...
echo   This speeds up first Claude Code startup.
echo.
echo   Caching: @modelcontextprotocol/server-filesystem...
call npm cache add @modelcontextprotocol/server-filesystem@2.1.0 >nul 2>nul
echo   Caching: chrome-devtools-mcp...
call npm cache add chrome-devtools-mcp@1.12.0 >nul 2>nul
echo   Caching: @aashari/mcp-server-atlassian-jira...
call npm cache add @aashari/mcp-server-atlassian-jira@3.3.0 >nul 2>nul
echo   Caching: @aashari/mcp-server-atlassian-confluence...
call npm cache add @aashari/mcp-server-atlassian-confluence@3.3.0 >nul 2>nul
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
echo 1. Set your API tokens as environment variables - do not edit them into .mcp.json:
echo    - ATLASSIAN_SITE_NAME (subdomain only), ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN (for Jira/Confluence)
echo    - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub)
echo    Store them in Windows Credential Manager and load them per session - see INSTALLATION.md
echo.
echo 2. Start Claude Code FROM THIS FOLDER:
echo    cd "%CD%"
echo    claude
echo.
echo 3. Inside Claude Code, verify MCP with: /mcp
echo.
echo 4. Run /aid-start to begin working!
echo.
echo 5. Cucumber BDD commands:
echo    npm run cucumber        - Run BDD acceptance tests
echo    npm run cucumber:dry    - Validate feature file syntax
echo    npm run test:bdd        - Run tests and generate HTML report
echo    npm run test:smoke      - Run @smoke tagged tests only
echo    npm run test:critical   - Run @critical tagged tests only
echo.
echo 6. (OPTIONAL^) Preview design spec components in Storybook:
echo    - Implement a component from the approved design specification
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
