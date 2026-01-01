@echo off
REM ============================================
REM AID - Figma Server Docker Setup
REM Auto-installs Docker Desktop if needed
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    Figma Server Docker Setup
echo ========================================
echo.

REM Configuration
set "DOCKER_INSTALLER_URL=https://desktop.docker.com/win/main/amd64/Docker Desktop Installer.exe"
set "DOCKER_INSTALLER_PATH=%TEMP%\DockerDesktopInstaller.exe"
set "FIGMA_SERVER_PATH=%~dp0integrations\figma-plugin\server"
set "MAX_WAIT_SECONDS=300"

REM ===========================================
REM STEP 1: Check if Docker is installed
REM ===========================================
echo [STEP 1/5] Checking Docker Desktop installation...

where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Docker CLI found
    goto :check_docker_running
)

REM Check if Docker Desktop is installed but not in PATH
if exist "%ProgramFiles%\Docker\Docker\resources\bin\docker.exe" (
    echo [OK] Docker Desktop installed but not in PATH
    set "PATH=%PATH%;%ProgramFiles%\Docker\Docker\resources\bin"
    goto :check_docker_running
)

echo [INFO] Docker Desktop not found - will install automatically
goto :install_docker

REM ===========================================
REM STEP 2: Install Docker Desktop
REM ===========================================
:install_docker
echo.
echo [STEP 2/5] Installing Docker Desktop...
echo This may take several minutes. Please wait...
echo.

REM Download Docker Desktop installer
echo Downloading Docker Desktop installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOCKER_INSTALLER_URL%' -OutFile '%DOCKER_INSTALLER_PATH%' -UseBasicParsing}" 2>nul
if %ERRORLEVEL% NEQ 0 (
    REM Fallback: try with curl
    echo [INFO] PowerShell download failed, trying curl...
    curl -L -o "%DOCKER_INSTALLER_PATH%" "%DOCKER_INSTALLER_URL%" 2>nul
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to download Docker Desktop installer
        echo.
        echo Please install Docker Desktop manually from:
        echo   https://www.docker.com/products/docker-desktop/
        echo.
        echo After installation, run this script again.
        pause
        exit /b 1
    )
)
echo [OK] Installer downloaded

REM Install Docker Desktop silently
echo.
echo Installing Docker Desktop silently...
echo (This requires administrator privileges)
echo.

REM Run installer with quiet mode and auto-accept
"%DOCKER_INSTALLER_PATH%" install --quiet --accept-license 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Silent install may have failed, trying interactive...
    "%DOCKER_INSTALLER_PATH%" install --accept-license
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Docker Desktop installation failed
        echo.
        echo Please install Docker Desktop manually from:
        echo   https://www.docker.com/products/docker-desktop/
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Docker Desktop installed successfully

REM Clean up installer
del "%DOCKER_INSTALLER_PATH%" 2>nul

REM Add Docker to PATH for this session
set "PATH=%PATH%;%ProgramFiles%\Docker\Docker\resources\bin"

echo.
echo [INFO] Docker Desktop installed. A restart may be required.
echo [INFO] If Docker fails to start, please restart your computer.
echo.

REM ===========================================
REM STEP 3: Start Docker Desktop
REM ===========================================
:check_docker_running
echo.
echo [STEP 3/5] Checking if Docker Desktop is running...

docker info >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Docker Desktop is running
    goto :build_container
)

echo [INFO] Starting Docker Desktop...

REM Start Docker Desktop
if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" (
    start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
) else (
    echo [ERROR] Docker Desktop executable not found
    echo Please start Docker Desktop manually and run this script again.
    pause
    exit /b 1
)

REM Wait for Docker to be ready
echo Waiting for Docker Desktop to be ready...
echo (This may take up to 5 minutes on first run)
echo.
set /a WAIT_COUNT=0
set /a WAIT_INTERVAL=5

:wait_docker_loop
if %WAIT_COUNT% GEQ %MAX_WAIT_SECONDS% (
    echo.
    echo [ERROR] Docker Desktop did not start within %MAX_WAIT_SECONDS% seconds
    echo.
    echo Possible solutions:
    echo   1. Restart your computer and try again
    echo   2. Open Docker Desktop manually first
    echo   3. Check Docker Desktop settings for errors
    echo.
    pause
    exit /b 1
)

docker info >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Docker Desktop is ready
    goto :build_container
)

REM Wait and increment counter (ping -n 6 = ~5 second delay)
ping -n 6 127.0.0.1 >nul 2>&1
set /a WAIT_COUNT+=%WAIT_INTERVAL%
echo   Waiting... (%WAIT_COUNT%s / %MAX_WAIT_SECONDS%s max)
goto :wait_docker_loop

REM ===========================================
REM STEP 4: Build Container
REM ===========================================
:build_container
echo.
echo [STEP 4/5] Building Figma server container...

REM Navigate to Figma server directory
pushd "%FIGMA_SERVER_PATH%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Figma server directory not found:
    echo   %FIGMA_SERVER_PATH%
    pause
    exit /b 1
)

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found in:
    echo   %FIGMA_SERVER_PATH%
    popd
    pause
    exit /b 1
)

REM Build the container
echo Building container image...
docker-compose build --no-cache
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build container
    echo.
    echo Try running manually:
    echo   cd "%FIGMA_SERVER_PATH%"
    echo   docker-compose build --no-cache
    echo.
    popd
    pause
    exit /b 1
)
echo [OK] Container built successfully

REM ===========================================
REM STEP 5: Start Container
REM ===========================================
echo.
echo [STEP 5/5] Starting Figma server container...

REM Stop any existing container first
docker-compose down 2>nul

REM Start container in detached mode
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start container
    echo.
    echo Try running manually:
    echo   cd "%FIGMA_SERVER_PATH%"
    echo   docker-compose up -d
    echo.
    popd
    pause
    exit /b 1
)

popd

REM Wait for health check
echo.
echo Waiting for server health check...
ping -n 11 127.0.0.1 >nul 2>&1

REM Verify server is healthy
docker inspect --format="{{.State.Health.Status}}" aid-figma-server 2>nul | findstr "healthy" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Figma server is healthy
) else (
    echo [INFO] Server may still be starting...
    echo       Check status with: docker ps
)

REM ===========================================
REM Complete
REM ===========================================
echo.
echo ========================================
echo    Figma Server Setup Complete!
echo ========================================
echo.
echo Container:  aid-figma-server
echo Port:       http://localhost:3001
echo Health:     http://localhost:3001/health
echo.
echo The server will AUTO-START with Docker Desktop.
echo.
echo Useful commands:
echo   docker logs aid-figma-server      - View logs
echo   docker restart aid-figma-server   - Restart server
echo   docker stop aid-figma-server      - Stop server
echo.
echo To pair with Figma plugin, run: /aid-pair
echo.
echo ========================================
echo.

exit /b 0
