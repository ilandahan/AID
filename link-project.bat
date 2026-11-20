@echo off
REM ============================================
REM AID - Link Project Script
REM Creates junctions/links from project to AID
REM Usage: link-project.bat [path] [--force] [--copy] [--role name-or-number]
REM NOTE: Uses junctions (no admin required)
REM Needs node (registers the AID hooks, T16 I-9) and python (creates the project
REM state through hooks\aid_session.py init, T16 I-10).
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    AID Project Linker (Windows)
echo ========================================
echo.

REM Get AID path (where this script is located)
set "AID_PATH=%~dp0"
set "AID_PATH=%AID_PATH:~0,-1%"

echo AID Installation: "!AID_PATH!"
echo.

REM Check for flags
set "FORCE_MODE=0"
set "COPY_MODE=0"
REM The role aid_session.py init starts the project with (a name or a menu number).
set "ROLE=1"
set "ROLE_NEXT=0"
set "TARGET_PATH="
for %%a in (%*) do (
    set "ARG_USED=0"
    if "!ROLE_NEXT!"=="1" (
        set "ROLE=%%~a"
        set "ROLE_NEXT=0"
        set "ARG_USED=1"
    )
    if "!ARG_USED!"=="0" (
        if /i "%%~a"=="--force" set "FORCE_MODE=1" & set "ARG_USED=1"
        if /i "%%~a"=="-f" set "FORCE_MODE=1" & set "ARG_USED=1"
        if /i "%%~a"=="--copy" set "COPY_MODE=1" & set "ARG_USED=1"
        if /i "%%~a"=="--role" set "ROLE_NEXT=1" & set "ARG_USED=1"
    )
    REM Get target project path (the first argument that is not a flag)
    if "!ARG_USED!"=="0" if "!TARGET_PATH!"=="" set "TARGET_PATH=%%~a"
)

REM The role is passed to aid_session.py and printed in a command line: accept only a
REM plain name or number.
set "ROLE_REST=#!ROLE!"
for %%c in (a b c d e f g h i j k l m n o p q r s t u v w x y z 0 1 2 3 4 5 6 7 8 9 _ -) do set "ROLE_REST=!ROLE_REST:%%c=!"
if "!ROLE!"=="" set "ROLE_REST=empty"
if not "!ROLE_REST!"=="#" (
    echo [ERROR] --role must be a role name or menu number - letters, digits, _ and -
    exit /b 1
)

REM If no path provided, ask for it
if "!TARGET_PATH!"=="" (
    set /p "TARGET_PATH=Enter project path to link: "
)

REM Remove trailing backslash if present
if "!TARGET_PATH:~-1!"=="\" set "TARGET_PATH=!TARGET_PATH:~0,-1!"

echo Target Project:   "!TARGET_PATH!"
if "!FORCE_MODE!"=="1" (
    echo Mode:             FORCE (will recreate links/copies^)
)
if "!COPY_MODE!"=="1" (
    echo Mode:             COPY (not using symlinks^)
)
echo.

REM Verify target exists
if not exist "!TARGET_PATH!" (
    echo [ERROR] Target folder does not exist: "!TARGET_PATH!"
    pause
    exit /b 1
)

REM ============================================
REM Refuse destructive targets
REM WHY: both the junction branch and the xcopy fallback below run
REM `rmdir /S /Q "!TARGET_PATH!\.claude\<dir>"` before creating the replacement.
REM If the target resolves to this AID install, that deletes AID's own
REM skills/agents/commands/references/rules - and `xcopy /I` then recreates the
REM folder EMPTY, so the failure looks like a successful link. If it resolves to
REM the user profile, it wipes their global .claude content.
REM Resolve both to full paths first: ".", a trailing slash and a mapped drive
REM all reach the same folder by different spellings.
REM ============================================
for %%I in ("!TARGET_PATH!") do set "TARGET_REAL=%%~fI"
for %%I in ("!AID_PATH!") do set "AID_REAL=%%~fI"

if /i "!TARGET_REAL!"=="!AID_REAL!" (
    echo [ERROR] Target is the AID installation itself:
    echo         "!TARGET_REAL!"
    echo.
    echo         Linking AID to itself deletes its own skills, agents and commands.
    echo         Pass a different project folder.
    pause
    exit /b 1
)

if /i "!TARGET_REAL!"=="!USERPROFILE!" (
    echo [ERROR] Target is your user profile folder:
    echo         "!TARGET_REAL!"
    echo.
    echo         This would replace your global .claude content with links to AID.
    echo         Pass a specific project folder instead.
    pause
    exit /b 1
)

REM Check for existing links and ask to update
if "!FORCE_MODE!"=="0" (
    if exist "!TARGET_PATH!\.claude" (
        echo Existing .claude folder detected.
        echo   [Y] Yes, recreate links/copies
        echo   [N] No, keep existing
        echo.
        set /p "UPDATE_CHOICE=Your choice (Y/N): "
        if /i "!UPDATE_CHOICE!"=="Y" set "FORCE_MODE=1"
        echo.
    )
)

REM ============================================
REM Verify AID's own content is intact BEFORE touching the target
REM WHY: every branch below deletes the target folder before recreating it. If a
REM source folder is missing, the delete removes the project's copy and puts
REM nothing back. Fail before the first rmdir, not after.
REM ============================================
for %%D in (commands skills agents references rules hooks) do (
    if not exist "!AID_PATH!\%%D" (
        echo [ERROR] AID installation is incomplete - missing %%D\
        echo         Nothing was changed in "!TARGET_PATH!".
        echo         Restore the AID folder before linking.
        pause
        exit /b 1
    )
)

REM ============================================
REM node is required (T16 I-9)
REM WHY: the hooks registered in the project's .claude\settings.json run `node`. A
REM project linked with gates that cannot run would look protected and not be. Stop
REM before anything is written.
REM ============================================
node -e "" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] node was not found on PATH.
    echo         AID's phase gates run with node; install Node.js and run link-project again.
    echo         Nothing was changed in "!TARGET_PATH!".
    pause
    exit /b 1
)

REM ============================================
REM Create .claude directory
REM ============================================
echo Creating .claude directory...
if not exist "!TARGET_PATH!\.claude" mkdir "!TARGET_PATH!\.claude"

REM ============================================
REM Create junctions OR copy (based on mode)
REM ============================================
if "!COPY_MODE!"=="1" (
    echo.
    echo Copying AID content to project...
    echo (You will need to re-run this script to get AID updates^)
    echo.
    goto :do_copy
)

echo.
echo Creating junctions to AID...
echo (Changes in AID will automatically apply to this project^)
echo.

REM Create junctions for directories (no admin required)
if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\commands" rmdir /S /Q "!TARGET_PATH!\.claude\commands" 2>nul
)
if not exist "!TARGET_PATH!\.claude\commands" (
    mklink /J "!TARGET_PATH!\.claude\commands" "!AID_PATH!\commands" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\commands -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for commands
    )
) else (
    echo   [SKIP] commands already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\skills" rmdir /S /Q "!TARGET_PATH!\.claude\skills" 2>nul
)
if not exist "!TARGET_PATH!\.claude\skills" (
    mklink /J "!TARGET_PATH!\.claude\skills" "!AID_PATH!\skills" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\skills -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for skills
    )
) else (
    echo   [SKIP] skills already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\agents" rmdir /S /Q "!TARGET_PATH!\.claude\agents" 2>nul
)
if not exist "!TARGET_PATH!\.claude\agents" (
    mklink /J "!TARGET_PATH!\.claude\agents" "!AID_PATH!\agents" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\agents -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for agents
    )
) else (
    echo   [SKIP] agents already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\references" rmdir /S /Q "!TARGET_PATH!\.claude\references" 2>nul
)
if not exist "!TARGET_PATH!\.claude\references" (
    mklink /J "!TARGET_PATH!\.claude\references" "!AID_PATH!\references" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\references -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for references
    )
) else (
    echo   [SKIP] references already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\rules" rmdir /S /Q "!TARGET_PATH!\.claude\rules" 2>nul
)
if not exist "!TARGET_PATH!\.claude\rules" (
    mklink /J "!TARGET_PATH!\.claude\rules" "!AID_PATH!\rules" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\rules -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for rules
    )
) else (
    echo   [SKIP] rules already exists
)

REM hooks MUST be linked: the settings.json copied later declares Stop and
REM PostToolUse hooks by the path .claude\hooks\*. Without this a linked project gets
REM a settings file pointing at scripts that are not there.
if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\hooks" rmdir /S /Q "!TARGET_PATH!\.claude\hooks" 2>nul
)
if not exist "!TARGET_PATH!\.claude\hooks" (
    mklink /J "!TARGET_PATH!\.claude\hooks" "!AID_PATH!\hooks" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] .claude\hooks -^> AID
    ) else (
        echo   [ERROR] Failed to create junction for hooks
    )
) else (
    echo   [SKIP] hooks already exists
)

REM For CLAUDE.md (file), try hard link first, fall back to copy
echo.
echo Linking CLAUDE.md...
if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\CLAUDE.md" del "!TARGET_PATH!\CLAUDE.md" 2>nul
)
if not exist "!TARGET_PATH!\CLAUDE.md" (
    mklink /H "!TARGET_PATH!\CLAUDE.md" "!AID_PATH!\CLAUDE.md" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [LINK] CLAUDE.md -^> AID (hard link^)
    ) else (
        REM Hard link failed (different drives?), copy instead
        copy "!AID_PATH!\CLAUDE.md" "!TARGET_PATH!\CLAUDE.md" >nul
        echo   [COPY] CLAUDE.md (different drives, copied^)
    )
) else (
    echo   [SKIP] CLAUDE.md already exists
)

goto :after_copy

REM ============================================
REM Copy mode (fallback when symlinks not available)
REM ============================================
:do_copy

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\commands" rmdir /S /Q "!TARGET_PATH!\.claude\commands" 2>nul
)
if not exist "!TARGET_PATH!\.claude\commands" (
    xcopy /E /I /Q "!AID_PATH!\commands" "!TARGET_PATH!\.claude\commands" >nul
    echo   [COPY] .claude\commands
) else (
    echo   [SKIP] commands already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\skills" rmdir /S /Q "!TARGET_PATH!\.claude\skills" 2>nul
)
if not exist "!TARGET_PATH!\.claude\skills" (
    xcopy /E /I /Q "!AID_PATH!\skills" "!TARGET_PATH!\.claude\skills" >nul
    echo   [COPY] .claude\skills
) else (
    echo   [SKIP] skills already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\agents" rmdir /S /Q "!TARGET_PATH!\.claude\agents" 2>nul
)
if not exist "!TARGET_PATH!\.claude\agents" (
    xcopy /E /I /Q "!AID_PATH!\agents" "!TARGET_PATH!\.claude\agents" >nul
    echo   [COPY] .claude\agents
) else (
    echo   [SKIP] agents already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\references" rmdir /S /Q "!TARGET_PATH!\.claude\references" 2>nul
)
if not exist "!TARGET_PATH!\.claude\references" (
    xcopy /E /I /Q "!AID_PATH!\references" "!TARGET_PATH!\.claude\references" >nul
    echo   [COPY] .claude\references
) else (
    echo   [SKIP] references already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\rules" rmdir /S /Q "!TARGET_PATH!\.claude\rules" 2>nul
)
if not exist "!TARGET_PATH!\.claude\rules" (
    xcopy /E /I /Q "!AID_PATH!\rules" "!TARGET_PATH!\.claude\rules" >nul
    echo   [COPY] .claude\rules
) else (
    echo   [SKIP] rules already exists
)

if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\.claude\hooks" rmdir /S /Q "!TARGET_PATH!\.claude\hooks" 2>nul
)
if not exist "!TARGET_PATH!\.claude\hooks" (
    xcopy /E /I /Q "!AID_PATH!\hooks" "!TARGET_PATH!\.claude\hooks" >nul
    echo   [COPY] .claude\hooks
) else (
    echo   [SKIP] hooks already exists
)

REM Copy CLAUDE.md
echo.
echo Copying CLAUDE.md...
if "!FORCE_MODE!"=="1" (
    if exist "!TARGET_PATH!\CLAUDE.md" del "!TARGET_PATH!\CLAUDE.md" 2>nul
)
if not exist "!TARGET_PATH!\CLAUDE.md" (
    copy "!AID_PATH!\CLAUDE.md" "!TARGET_PATH!\CLAUDE.md" >nul
    echo   [COPY] CLAUDE.md
) else (
    echo   [SKIP] CLAUDE.md already exists
)

:after_copy

REM ============================================
REM Copy project-specific files (always copied)
REM ============================================
echo.
echo Copying project-specific files...

REM Register the AID hooks in the project's settings.json (T16 I-9). The ONE generator is
REM scripts\link-settings.mjs: it reads .claude-plugin\plugin.json, keeps the user's own
REM keys and hooks, and leaves an unparseable file untouched (and fails).
node "!AID_REAL!\scripts\link-settings.mjs" "!TARGET_REAL!" "!AID_REAL!"
if errorlevel 1 (
    echo   [ERROR] .claude\settings.json was not updated: the AID hooks are NOT registered.
    echo           Fix the problem above and run link-project again.
    pause
    exit /b 1
)

REM ============================================
REM Create .aid directory structure
REM ============================================
echo.
echo Creating project state directory...
if not exist "!TARGET_PATH!\.aid" mkdir "!TARGET_PATH!\.aid"
if not exist "!TARGET_PATH!\.aid\qa" mkdir "!TARGET_PATH!\.aid\qa"

REM The project state is created ONLY by hooks\aid_session.py (T16 I-10, E3): this
REM script runs its `init`, with cwd and CLAUDE_PROJECT_DIR = the target, and never
REM writes state.json or context.json itself. init also creates .aid\context.json.
if exist "!TARGET_PATH!\.aid\state.json" (
    echo   [SKIP] state.json already exists
    goto :after_state
)
REM python3, python, py -3; the Windows Store stub exits 9009, so only a python that
REM really runs counts.
set "PY_CMD="
python3 -c "import sys" >nul 2>&1 && set "PY_CMD=python3"
if not defined PY_CMD python -c "import sys" >nul 2>&1 && set "PY_CMD=python"
if not defined PY_CMD py -3 -c "import sys" >nul 2>&1 && set "PY_CMD=py -3"
set "INIT_RC=1"
if defined PY_CMD (
    pushd "!TARGET_REAL!"
    set "CLAUDE_PROJECT_DIR=!TARGET_REAL!"
    !PY_CMD! "!AID_REAL!\hooks\aid_session.py" init !ROLE! 0
    set "INIT_RC=!ERRORLEVEL!"
    set "CLAUDE_PROJECT_DIR="
    popd
)
if "!INIT_RC!"=="0" if exist "!TARGET_PATH!\.aid\state.json" (
    echo   [OK] state.json created by aid_session.py init
    goto :after_state
)
if not defined PY_CMD (
    echo   [WARNING] No working python found - tried python3, python, py -3.
    set "PY_CMD=python"
) else (
    echo   [WARNING] aid_session.py init failed - exit !INIT_RC!.
)
REM R1-09: init resolves to the nearest AID root above the target (INV-2) and refuses
REM there, so the printed command would fail the same way. Name that ancestor.
set "AID_ANCESTOR="
call :find_aid_ancestor "!TARGET_REAL!"
if defined AID_ANCESTOR (
    echo   [WARNING] The project is inside another AID project: !AID_ANCESTOR!
    echo   [WARNING] init uses that project's state and refuses; the command below fails
    echo             the same way until the project is moved out of !AID_ANCESTOR!.
)
echo   [WARNING] The project state was NOT created. Run this yourself in the project:
echo       cd /d "!TARGET_REAL!"
echo       !PY_CMD! "!AID_REAL!\hooks\aid_session.py" init !ROLE! 0
:after_state

REM ============================================
REM Create docs directory structure
REM ============================================
echo.
echo Creating docs directories (phase outputs)...
if not exist "!TARGET_PATH!\docs" mkdir "!TARGET_PATH!\docs"
if not exist "!TARGET_PATH!\docs\research" mkdir "!TARGET_PATH!\docs\research"
if not exist "!TARGET_PATH!\docs\prd" mkdir "!TARGET_PATH!\docs\prd"
if not exist "!TARGET_PATH!\docs\tech-spec" mkdir "!TARGET_PATH!\docs\tech-spec"
if not exist "!TARGET_PATH!\docs\implementation-plan" mkdir "!TARGET_PATH!\docs\implementation-plan"
echo   [OK] docs/ structure created

REM ============================================
REM Copy .mcp.json template
REM ============================================
echo.
echo Copying MCP configuration...
if not exist "!TARGET_PATH!\.mcp.json" (
    if exist "!AID_PATH!\.mcp.json.windows" (
        copy "!AID_PATH!\.mcp.json.windows" "!TARGET_PATH!\.mcp.json" >nul
        echo   [COPY] .mcp.json - reads tokens from environment variables
    ) else (
        echo   [ERROR] .mcp.json.windows template not found
    )
) else (
    echo   [SKIP] .mcp.json already exists - kept; tokens come from environment variables / OS keystore, not this file
)
REM .mcp.json is per-user config and .aid/audit/ is the hook audit log: keep both out of
REM the project's git history. T17 I-26: the one helper, shared with link-project.sh, adds
REM a line only when no existing line equals it (a trailing CR, spaces and tabs ignored),
REM in the file's own line ending, so any mix of sh/bat runs adds it once.
node "!AID_REAL!\scripts\ensure-gitignore.mjs" "!TARGET_REAL!" ".mcp.json" ".aid/audit/"
if errorlevel 1 echo   [WARNING] .gitignore was not updated: add .mcp.json and .aid/audit/ to it yourself

REM ============================================
REM Summary
REM ============================================
echo.
echo ========================================
echo    Project Linked Successfully
echo ========================================
echo.
echo Target: "!TARGET_PATH!"
echo.
if "!COPY_MODE!"=="1" (
    echo AID content (COPIED - re-run to update^):
    echo   .claude\commands\   - Slash commands
    echo   .claude\skills\     - Phase skills
    echo   .claude\agents\     - Sub-agents
    echo   .claude\references\ - Reference docs
    echo   .claude\rules\      - Rules
    echo   CLAUDE.md           - AID instructions
    echo.
    echo NOTE: Files were COPIED, not linked.
    echo       To get AID updates, re-run: link-project.bat --force
) else (
    echo Junctions (auto-update from AID^):
    echo   .claude\commands\   -^> AID
    echo   .claude\skills\     -^> AID
    echo   .claude\agents\     -^> AID
    echo   .claude\references\ -^> AID
    echo   .claude\rules\      -^> AID
    echo   CLAUDE.md           -^> AID
)
echo.
echo Project-specific (not linked):
echo   .claude\settings.json - Permissions + AID hooks (phase gates)
echo   .aid\state.json       - Phase tracking (aid_session.py init)
echo   .aid\context.json     - Work context (aid_session.py init)
echo   .mcp.json             - MCP config (tokens come from environment variables / OS keystore, not this file)
echo   docs\                 - Phase outputs
echo.
echo Next steps:
echo.
echo 1. Set your API tokens as environment variables - see INSTALLATION.md; .mcp.json reads them
echo.
echo 2. Open Claude Code in the project:
echo    cd "!TARGET_PATH!"
echo    claude
echo.
echo 3. /aid-start, /aid-status, /phase-approve and /phase-advance need the plugin
echo    - claude plugin install aid@AID. Without it, run the session steps yourself
echo    in Claude Code, starting the line with an exclamation mark, for example:
echo    python "!AID_PATH!\hooks\aid_session.py" status   - also: start, approve, advance
echo.
echo ========================================
echo.
pause
goto :eof

REM Sets AID_ANCESTOR to the nearest folder above %1 whose .aid holds state.json or
REM hooks\config.json (an AID project root). The user-level .aid (USERPROFILE, AID_HOME)
REM is not a project and is skipped.
:find_aid_ancestor
set "FA_DIR=%~f1"
:fa_loop
for %%P in ("!FA_DIR!\..") do set "FA_PARENT=%%~fP"
if /i "!FA_PARENT!"=="!FA_DIR!" goto :eof
set "FA_DIR=!FA_PARENT!"
if "!FA_DIR:~-1!"=="\" (set "FA_AID=!FA_DIR!.aid") else (set "FA_AID=!FA_DIR!\.aid")
if not exist "!FA_AID!\state.json" if not exist "!FA_AID!\hooks\config.json" goto fa_loop
if /i "!FA_AID!"=="%USERPROFILE%\.aid" goto fa_loop
if defined AID_HOME if /i "!FA_AID!"=="%AID_HOME%" goto fa_loop
set "AID_ANCESTOR=!FA_DIR!"
goto :eof
