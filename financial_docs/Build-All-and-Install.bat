@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ========================================================
:: FINANCIAL HUB BUILD SYSTEM v3.0 - UNIVERSAL EDITION
:: Combines enterprise features with universal compatibility
:: ========================================================

:: Get script location with proper handling of spaces and special chars
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=%~nx0"
set "SCRIPT_FULL_PATH=%~f0"

:: Detect PowerShell availability and version
set "PS_AVAILABLE=0"
set "PS_VERSION=0"
where powershell >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PS_AVAILABLE=1"
    for /f "tokens=*" %%v in ('powershell -NoProfile -Command "$PSVersionTable.PSVersion.Major" 2^>nul') do set "PS_VERSION=%%v"
)

:: Detect Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set "WIN_VER=%%i.%%j"
set "IS_WIN11=0"
for /f "tokens=3" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild 2^>nul ^| find "CurrentBuild"') do (
    if %%a GEQ 22000 set "IS_WIN11=1"
)

:: Get locale-independent timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "dt=%%I"
if defined dt (
    set "TIMESTAMP=%dt:~0,8%_%dt:~8,6%"
) else (
    :: Fallback if WMIC not available (newer Windows 11 versions)
    set "TIMESTAMP=%random%_%random%"
)

:: Initialize logging with safe path handling
set "LOG_DIR=%SCRIPT_DIR%logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" 2>nul

:: Check if we can write to log directory
echo. > "%LOG_DIR%\test.tmp" 2>nul
if %ERRORLEVEL% NEQ 0 (
    :: Can't write to script directory, use TEMP
    set "LOG_DIR=%TEMP%\financial_hub_logs"
    if not exist "!LOG_DIR!" mkdir "!LOG_DIR!" 2>nul
)
del "%LOG_DIR%\test.tmp" 2>nul

set "LOG_FILE=%LOG_DIR%\build_%TIMESTAMP%.log"
set "ERROR_LOG=%LOG_DIR%\errors_%TIMESTAMP%.log"

:: Initialize log file
(
    echo ========================================================
    echo FINANCIAL HUB BUILD SYSTEM STARTED
    echo Timestamp: %TIMESTAMP%
    echo Script: %SCRIPT_FULL_PATH%
    echo Windows Version: %WIN_VER%
    echo Windows 11: %IS_WIN11%
    echo PowerShell: %PS_AVAILABLE% (v%PS_VERSION%^)
    echo ========================================================
) > "%LOG_FILE%" 2>nul

goto :MAIN

:: ========================================================
:: COLOR HELPER FUNCTIONS - Enhanced for compatibility
:: ========================================================

:COLOR_SUCCESS
    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "Write-Host '[SUCCESS]' -ForegroundColor Green -NoNewline; Write-Host ' %~1'" 2>nul
        if !ERRORLEVEL! NEQ 0 echo [SUCCESS] %~1
    ) else (
        echo [SUCCESS] %~1
    )
    echo [SUCCESS] %~1 >> "%LOG_FILE%" 2>nul
    exit /b

:COLOR_INFO
    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "Write-Host '[INFO]' -ForegroundColor Cyan -NoNewline; Write-Host ' %~1'" 2>nul
        if !ERRORLEVEL! NEQ 0 echo [INFO] %~1
    ) else (
        echo [INFO] %~1
    )
    echo [INFO] %~1 >> "%LOG_FILE%" 2>nul
    exit /b

:COLOR_WARNING
    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "Write-Host '[WARNING]' -ForegroundColor Yellow -NoNewline; Write-Host ' %~1'" 2>nul
        if !ERRORLEVEL! NEQ 0 echo [WARNING] %~1
    ) else (
        echo [WARNING] %~1
    )
    echo [WARNING] %~1 >> "%LOG_FILE%" 2>nul
    echo [WARNING] %~1 >> "%ERROR_LOG%" 2>nul
    exit /b

:COLOR_ERROR
    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "Write-Host '[ERROR]' -ForegroundColor Red -NoNewline; Write-Host ' %~1'" 2>nul
        if !ERRORLEVEL! NEQ 0 echo [ERROR] %~1
    ) else (
        echo [ERROR] %~1
    )
    echo [ERROR] %~1 >> "%LOG_FILE%" 2>nul
    echo [ERROR] %~1 >> "%ERROR_LOG%" 2>nul
    exit /b

:COLOR_STEP
    echo.
    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "Write-Host '========================================' -ForegroundColor Magenta" 2>nul
        powershell -NoProfile -Command "Write-Host ' %~1' -ForegroundColor Magenta" 2>nul
        powershell -NoProfile -Command "Write-Host '========================================' -ForegroundColor Magenta" 2>nul
        if !ERRORLEVEL! NEQ 0 (
            echo ========================================
            echo  %~1
            echo ========================================
        )
    ) else (
        echo ========================================
        echo  %~1
        echo ========================================
    )
    echo.
    echo ======================================== >> "%LOG_FILE%" 2>nul
    echo  %~1 >> "%LOG_FILE%" 2>nul
    echo ======================================== >> "%LOG_FILE%" 2>nul
    exit /b

:SHOW_PROGRESS
    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "Write-Host '[PROGRESS]' -ForegroundColor Blue -NoNewline; Write-Host ' %~1'" 2>nul
        if !ERRORLEVEL! NEQ 0 echo [PROGRESS] %~1
    ) else (
        echo [PROGRESS] %~1
    )
    echo [PROGRESS] %~1 >> "%LOG_FILE%" 2>nul
    exit /b

:COUNTDOWN
    set /a seconds=%~1
    echo.
    call :COLOR_INFO "Waiting %seconds% seconds..."
    for /l %%i in (%seconds%,-1,1) do (
        <nul set /p "=%%i... "
        timeout /t 1 /nobreak >nul 2>&1
        if !ERRORLEVEL! NEQ 0 ping 127.0.0.1 -n 2 >nul
    )
    echo.
    exit /b

:DRAW_BOX
    echo.
    echo ============================================================
    echo  %~1
    echo ============================================================
    echo.
    exit /b

:: ========================================================
:: MAIN EXECUTION
:: ========================================================
:MAIN

cls
echo.
call :DRAW_BOX "WELCOME TO FINANCIAL HUB BUILDER v3.0"

if %PS_AVAILABLE%==1 (
    powershell -NoProfile -Command "Write-Host 'This tool will automatically:' -ForegroundColor Green" 2>nul
    if !ERRORLEVEL! EQU 0 (
        powershell -NoProfile -Command "Write-Host '  * Check your system is ready' -ForegroundColor White" 2>nul
        powershell -NoProfile -Command "Write-Host '  * Install Python if needed' -ForegroundColor White" 2>nul
        powershell -NoProfile -Command "Write-Host '  * Set up your project environment' -ForegroundColor White" 2>nul
        powershell -NoProfile -Command "Write-Host '  * Build your Financial Hub dashboard' -ForegroundColor White" 2>nul
        echo.
        powershell -NoProfile -Command "Write-Host 'No technical knowledge required!' -ForegroundColor Yellow" 2>nul
    ) else (
        goto :BASIC_WELCOME
    )
) else (
    :BASIC_WELCOME
    echo This tool will automatically:
    echo   * Check your system is ready
    echo   * Install Python if needed
    echo   * Set up your project environment
    echo   * Build your Financial Hub dashboard
    echo.
    echo No technical knowledge required!
)

echo Just sit back and let the system do the work.
echo.
pause

call :COLOR_STEP "SYSTEM INFORMATION"
call :COLOR_INFO "Operating System: %OS%"
call :COLOR_INFO "Windows Version: %WIN_VER%"
if %IS_WIN11%==1 (
    call :COLOR_INFO "Windows 11 Detected"
)
call :COLOR_INFO "Computer Name: %COMPUTERNAME%"
call :COLOR_INFO "User: %USERNAME%"
call :COLOR_INFO "Script Location: %SCRIPT_DIR%"
call :COLOR_INFO "PowerShell Available: %PS_AVAILABLE%"

:: ========================================================
:: STEP 0: PRE-FLIGHT CHECKS
:: ========================================================
call :COLOR_STEP "STEP 0: Pre-Flight Checks"

:: Check administrator privileges
call :SHOW_PROGRESS "Checking administrator privileges..."
set "IS_ADMIN=0"
net session >nul 2>&1
if %ERRORLEVEL% EQU 0 set "IS_ADMIN=1"

if %IS_ADMIN% EQU 0 (
    call :COLOR_WARNING "Not running as administrator"
    echo.
    echo Some operations may require administrator access.
    echo.
    echo Do you want to restart with administrator privileges?
    echo [Y] Yes - Restart as administrator
    echo [N] No  - Continue anyway (recommended if Python is already installed)
    echo.
    set /p "NEED_ADMIN=Your choice (Y/N): "

    if /i "!NEED_ADMIN!"=="Y" (
        echo.
        echo Restarting with administrator privileges...
        powershell -NoProfile -Command "Start-Process -FilePath '%SCRIPT_FULL_PATH%' -Verb RunAs" 2>nul
        if !ERRORLEVEL! NEQ 0 (
            echo Failed to elevate. Please right-click and select "Run as administrator"
            pause
        )
        exit /b 0
    ) else (
        call :COLOR_INFO "Continuing without administrator privileges"
    )
) else (
    call :COLOR_SUCCESS "Running with administrator privileges"
)

:: Check path type
call :SHOW_PROGRESS "Analyzing installation path..."
set "PATH_WARNING=0"

:: Check for UNC path
echo "%SCRIPT_DIR%" | find "\\\\" >nul 2>&1
if %ERRORLEVEL%==0 (
    call :COLOR_WARNING "Running from network path (UNC)"
    call :COLOR_INFO "Local installation is recommended for best performance"
    set "PATH_WARNING=1"
)

:: Check for spaces (warn but don't block - modern Python handles this)
echo "%SCRIPT_DIR%" | findstr /c:" " >nul 2>&1
if %ERRORLEVEL% == 0 (
    call :COLOR_INFO "Path contains spaces (this is fine for Python 3.8+)"
    echo Modern Python handles spaces correctly.
    set "PATH_WARNING=1"
)

:: Check for extremely long paths
set "PATH_LENGTH=0"
set "TEMP_PATH=%SCRIPT_DIR%"
:COUNT_PATH_LENGTH
if defined TEMP_PATH (
    set "TEMP_PATH=%TEMP_PATH:~1%"
    set /a PATH_LENGTH+=1
    goto :COUNT_PATH_LENGTH
)

if %PATH_LENGTH% GTR 200 (
    call :COLOR_WARNING "Very long path detected (%PATH_LENGTH% chars)"
    call :COLOR_INFO "Windows has a 260 character limit for full file paths"
    call :COLOR_INFO "If build fails, try moving to a shorter path like C:\FinancialHub\"
    set "PATH_WARNING=1"
)

if %PATH_WARNING%==0 (
    call :COLOR_SUCCESS "Installation path is optimal"
)

:: Check write permissions
call :SHOW_PROGRESS "Checking write permissions..."
echo test > "%SCRIPT_DIR%test_write.tmp" 2>nul
if %ERRORLEVEL% NEQ 0 (
    call :COLOR_ERROR "Cannot write to current directory!"
    call :DRAW_BOX "PERMISSION ERROR"
    echo The script cannot write files to:
    echo "%SCRIPT_DIR%"
    echo.
    echo Possible solutions:
    echo 1. Run as administrator (right-click script, "Run as administrator")
    echo 2. Move to a different folder (like C:\Projects\FinancialHub\)
    echo 3. Check folder permissions in Windows Explorer
    echo.
    pause
    exit /b 1
) else (
    del "%SCRIPT_DIR%test_write.tmp" >nul 2>&1
    call :COLOR_SUCCESS "Write permissions OK"
)

:: Check available disk space
call :SHOW_PROGRESS "Checking available disk space..."
set "FREE_SPACE_GB=Unknown"

:: Get drive letter from script path
set "DRIVE_LETTER=%SCRIPT_DIR:~0,2%"

:: Try using WMIC (works on most systems)
for /f "skip=1 tokens=3" %%a in ('wmic logicaldisk where "DeviceID='%DRIVE_LETTER%'" get FreeSpace 2^>nul') do (
    if not "%%a"=="" (
        set "FREE_BYTES=%%a"
        set /a "FREE_SPACE_GB=!FREE_BYTES:~0,-9!"
        goto :SPACE_CHECK_DONE
    )
)

:: Fallback: Try PowerShell
if %PS_AVAILABLE%==1 (
    for /f "usebackq tokens=*" %%a in (`powershell -NoProfile -Command "(Get-PSDrive '%DRIVE_LETTER:~0,1%' -ErrorAction SilentlyContinue).Free/1GB -as [int]" 2^>nul`) do (
        set "FREE_SPACE_GB=%%a"
        goto :SPACE_CHECK_DONE
    )
)

:SPACE_CHECK_DONE
if "%FREE_SPACE_GB%"=="Unknown" (
    call :COLOR_WARNING "Could not determine disk space"
) else (
    if %FREE_SPACE_GB% LSS 1 (
        call :COLOR_ERROR "Very low disk space: %FREE_SPACE_GB% GB available"
        call :COLOR_WARNING "Build may fail if space runs out"
        echo.
        set /p "CONTINUE_LOW_SPACE=Continue anyway? (Y/N): "
        if /i "!CONTINUE_LOW_SPACE!" NEQ "Y" exit /b 1
    ) else if %FREE_SPACE_GB% LSS 5 (
        call :COLOR_WARNING "Low disk space: %FREE_SPACE_GB% GB available"
    ) else (
        call :COLOR_SUCCESS "Disk space OK: %FREE_SPACE_GB% GB available"
    )
)

:: Check internet connection
call :SHOW_PROGRESS "Checking internet connection..."
set "INTERNET_OK=0"

:: Try multiple methods
ping -n 1 -w 1000 8.8.8.8 >nul 2>&1
if %ERRORLEVEL% EQU 0 set "INTERNET_OK=1"

if %INTERNET_OK% EQU 0 (
    ping -n 1 -w 1000 1.1.1.1 >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "INTERNET_OK=1"
)

if %INTERNET_OK% EQU 0 if %PS_AVAILABLE%==1 (
    powershell -NoProfile -Command "Test-Connection -ComputerName google.com -Count 1 -Quiet" 2>nul | find "True" >nul
    if !ERRORLEVEL! EQU 0 set "INTERNET_OK=1"
)

if %INTERNET_OK% EQU 0 (
    call :COLOR_WARNING "Internet connection check failed"
    echo.
    echo Internet is needed to download Python if not installed.
    echo If Python is already installed, you can continue safely.
    echo.
    set /p "CONTINUE_NO_NET=Continue anyway? (Y/N): "
    if /i "!CONTINUE_NO_NET!" NEQ "Y" exit /b 1
) else (
    call :COLOR_SUCCESS "Internet connection confirmed"
)

echo.
call :COLOR_SUCCESS "Pre-flight checks complete!"
echo.

:: ========================================================
:: STEP 1: PYTHON INSTALLATION & VERIFICATION
:: ========================================================
call :COLOR_STEP "STEP 1: Python Environment Setup"

call :SHOW_PROGRESS "Looking for Python on your computer..."

:: Check for Python in multiple ways
set "PYTHON_FOUND=0"
set "PYTHON_CMD=python"
set "PYTHON_VERSION="
set "PYTHON_MAJOR=0"
set "PYTHON_MINOR=0"

:: Try standard python command
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_FOUND=1"
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%V"
    goto :PYTHON_VERSION_CHECK
)

:: Try python3 command
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_FOUND=1"
    set "PYTHON_CMD=python3"
    for /f "tokens=2" %%V in ('python3 --version 2^>^&1') do set "PYTHON_VERSION=%%V"
    goto :PYTHON_VERSION_CHECK
)

:: Try py launcher (Windows)
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_FOUND=1"
    set "PYTHON_CMD=py"
    for /f "tokens=2" %%V in ('py --version 2^>^&1') do set "PYTHON_VERSION=%%V"
    goto :PYTHON_VERSION_CHECK
)

:PYTHON_VERSION_CHECK
if %PYTHON_FOUND%==1 (
    call :COLOR_SUCCESS "Python found: %PYTHON_VERSION%"

    :: Parse version
    for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
        set "PYTHON_MAJOR=%%a"
        set "PYTHON_MINOR=%%b"
    )

    :: Check minimum version (3.8+)
    if !PYTHON_MAJOR! LSS 3 (
        call :COLOR_WARNING "Python !PYTHON_VERSION! is too old (need 3.8+)"
        set "PYTHON_FOUND=0"
    ) else if !PYTHON_MAJOR! EQU 3 (
        if !PYTHON_MINOR! LSS 8 (
            call :COLOR_WARNING "Python !PYTHON_VERSION! is too old (need 3.8+)"
            set "PYTHON_FOUND=0"
        )
    )
)

if %PYTHON_FOUND%==0 (
    call :COLOR_WARNING "Python 3.8+ not found on this system"
    echo.
    echo Python needs to be installed.
    echo.

    :: Try winget first (Windows 11 / modern Windows 10)
    call :SHOW_PROGRESS "Checking for Windows Package Manager (winget)..."
    where winget >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        call :COLOR_INFO "winget is available - using recommended method"
        echo.
        echo Installing Python via Windows Package Manager...
        echo This is the cleanest and most reliable installation method.
        echo.

        winget install --id Python.Python.3.12 --source winget --silent --accept-package-agreements --accept-source-agreements

        if !ERRORLEVEL! EQU 0 (
            call :COLOR_SUCCESS "Python installed successfully via winget!"
            echo.
            call :COLOR_INFO "IMPORTANT: Close this window and run the script again"
            call :COLOR_INFO "This refreshes the environment variables"
            echo.
            pause
            exit /b 0
        ) else (
            call :COLOR_WARNING "winget installation failed, trying alternative method..."
        )
    ) else (
        call :COLOR_INFO "winget not available (normal for older Windows 10)"
    )

    :: Fallback: Direct download
    call :COLOR_INFO "Downloading Python installer..."
    echo.

    set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"

    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "$ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'" 2>nul
    ) else (
        :: Fallback: use certutil (available on all Windows)
        certutil -urlcache -split -f "%PYTHON_URL%" "%PYTHON_INSTALLER%" >nul 2>&1
    )

    if exist "%PYTHON_INSTALLER%" (
        call :COLOR_SUCCESS "Download complete!"
        echo.
        echo Installing Python 3.12.7...
        echo.
        echo The installer will:
        echo   - Install Python for %USERNAME%
        echo   - Add Python to PATH
        echo   - Install pip package manager
        echo.
        echo This may take a few minutes...
        echo.

        :: Try all-users installation if admin, otherwise current user only
        if %IS_ADMIN% EQU 1 (
            "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_test=0
        ) else (
            "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
        )

        set "INSTALL_RESULT=!ERRORLEVEL!"
        del "%PYTHON_INSTALLER%" >nul 2>&1

        if !INSTALL_RESULT! EQU 0 (
            call :COLOR_SUCCESS "Python installation complete!"
            echo.
            call :COLOR_INFO "IMPORTANT: Close this window and run the script again"
            call :COLOR_INFO "This refreshes the environment variables"
            echo.
            pause
            exit /b 0
        ) else (
            call :COLOR_ERROR "Installation failed"
            echo.
            echo Please try manual installation:
            echo 1. Visit: https://www.python.org/downloads/
            echo 2. Download Python 3.12 or newer
            echo 3. Run installer and check "Add Python to PATH"
            echo 4. Run this script again
            echo.
            pause
            exit /b 1
        )
    ) else (
        call :COLOR_ERROR "Could not download Python installer"
        echo.
        echo Please install manually:
        echo 1. Visit: https://www.python.org/downloads/
        echo 2. Download Python 3.12 or newer
        echo 3. Run installer and check "Add Python to PATH"
        echo 4. Run this script again
        echo.
        pause
        exit /b 1
    )
)

:: ========================================================
:: STEP 2: VIRTUAL ENVIRONMENT SETUP
:: ========================================================
call :COLOR_STEP "STEP 2: Setting Up Isolated Environment"

echo Creating a clean workspace for your project...
echo This prevents conflicts with other Python installations.
echo.

set "VENV_DIR=%SCRIPT_DIR%venv"

IF NOT EXIST "%VENV_DIR%" (
    call :SHOW_PROGRESS "Creating virtual environment..."
    "%PYTHON_CMD%" -m venv "%VENV_DIR%"

    if !ERRORLEVEL! NEQ 0 (
        call :COLOR_ERROR "Failed to create virtual environment"
        call :COLOR_INFO "Trying to install venv module..."

        "%PYTHON_CMD%" -m pip install virtualenv
        "%PYTHON_CMD%" -m virtualenv "%VENV_DIR%"

        if !ERRORLEVEL! NEQ 0 (
            call :COLOR_ERROR "Could not create virtual environment"
            echo.
            echo Continuing without virtual environment (not recommended)
            echo.
            set "VENV_DIR="
            pause
        ) else (
            call :COLOR_SUCCESS "Virtual environment created using virtualenv"
        )
    ) else (
        call :COLOR_SUCCESS "Virtual environment created"
    )
) ELSE (
    call :COLOR_INFO "Virtual environment already exists"
)

:: Activate virtual environment if it exists
if defined VENV_DIR (
    if exist "%VENV_DIR%\Scripts\activate.bat" (
        call :SHOW_PROGRESS "Activating virtual environment..."
        call "%VENV_DIR%\Scripts\activate.bat"

        if !ERRORLEVEL! NEQ 0 (
            call :COLOR_WARNING "Failed to activate virtual environment"
            call :COLOR_INFO "Continuing with system Python"
        ) else (
            call :COLOR_SUCCESS "Virtual environment activated"

            :: Update PYTHON_CMD to use venv python
            set "PYTHON_CMD=%VENV_DIR%\Scripts\python.exe"
        )
    )
)

:: ========================================================
:: STEP 3: DEPENDENCY INSTALLATION
:: ========================================================
call :COLOR_STEP "STEP 3: Installing Required Components"

echo Installing project dependencies...
echo.

call :SHOW_PROGRESS "Upgrading pip to latest version..."
"%PYTHON_CMD%" -m pip install --upgrade pip --quiet 2>nul

set "MAX_RETRIES=3"
set "RETRY_COUNT=0"

:INSTALL_DEPENDENCIES
set /a RETRY_COUNT+=1

:: Check for requirements-dev.txt first, then requirements.txt
set "REQ_FILE=%SCRIPT_DIR%requirements-dev.txt"
if not exist "%REQ_FILE%" set "REQ_FILE=%SCRIPT_DIR%requirements.txt"

IF EXIST "%REQ_FILE%" (
    call :SHOW_PROGRESS "Installing from %REQ_FILE:~-20% (Attempt %RETRY_COUNT%/%MAX_RETRIES%)..."

    "%PYTHON_CMD%" -m pip install -r "%REQ_FILE%"

    if !ERRORLEVEL! NEQ 0 (
        call :COLOR_ERROR "Installation failed (Attempt %RETRY_COUNT%)"

        if %RETRY_COUNT% LSS %MAX_RETRIES% (
            echo Retrying in 5 seconds...
            call :COUNTDOWN 5
            goto :INSTALL_DEPENDENCIES
        ) else (
            call :COLOR_ERROR "Failed after %MAX_RETRIES% attempts"
            echo.
            call :COLOR_WARNING "Build may fail without dependencies"
            echo.
            set /p "CONTINUE_NO_DEPS=Continue anyway? (Y/N): "
            if /i "!CONTINUE_NO_DEPS!" NEQ "Y" exit /b 1
        )
    ) else (
        call :COLOR_SUCCESS "All components installed successfully"
    )
) ELSE (
    call :COLOR_WARNING "No requirements file found"
    call :COLOR_INFO "Installing PyInstaller as fallback..."
    "%PYTHON_CMD%" -m pip install pyinstaller --quiet 2>nul
    call :COLOR_SUCCESS "PyInstaller installed"
)

:: ========================================================
:: STEP 4: PROJECT STRUCTURE & INITIALIZATION
:: ========================================================
call :COLOR_STEP "STEP 4: Preparing Project Structure"

call :SHOW_PROGRESS "Creating directory structure..."

:: Create directories with error handling
set "DIRS_TO_CREATE=Archive\reports Archive\processed Archive\raw\exports"

for %%D in (%DIRS_TO_CREATE%) do (
    if not exist "%SCRIPT_DIR%%%D" (
        mkdir "%SCRIPT_DIR%%%D" 2>nul
        if !ERRORLEVEL! EQU 0 (
            call :COLOR_INFO "Created: %%D"
        ) else (
            call :COLOR_WARNING "Could not create: %%D"
        )
    )
)

call :SHOW_PROGRESS "Initializing configuration files..."

:: Create default config files if they don't exist (for first-time users)
IF NOT EXIST "%SCRIPT_DIR%Archive\processed\financial_config.json" (
    (
        echo {
        echo   "metadata": {"last_updated": "1970-01-01", "version": "2.0"},
        echo   "cash_accounts": {},
        echo   "credit_cards": {},
        echo   "debt_balances": {},
        echo   "recurring_expenses": {}
        echo }
    ) > "%SCRIPT_DIR%Archive\processed\financial_config.json"
    call :COLOR_INFO "Created default financial_config.json"
)

IF NOT EXIST "%SCRIPT_DIR%Archive\processed\budget.json" (
    (
        echo {
        echo   "metadata": {"total_spending_budget": 5000, "last_updated": "1970-01-01"},
        echo   "monthly_income": {"earnings": 7500},
        echo   "category_budgets": {}
        echo }
    ) > "%SCRIPT_DIR%Archive\processed\budget.json"
    call :COLOR_INFO "Created default budget.json"
)

IF NOT EXIST "%SCRIPT_DIR%Archive\processed\financial_goals.json" (
    (
        echo {
        echo   "goals": {},
        echo   "metadata": {"last_updated": "1970-01-01"}
        echo }
    ) > "%SCRIPT_DIR%Archive\processed\financial_goals.json"
    call :COLOR_INFO "Created default financial_goals.json"
)

IF NOT EXIST "%SCRIPT_DIR%Archive\raw\exports\AllTransactions.csv" (
    echo Date,Name,Amount,Category,Account Name,Description,Custom Name,Ignored From > "%SCRIPT_DIR%Archive\raw\exports\AllTransactions.csv"
    call :COLOR_INFO "Created default AllTransactions.csv"
)

IF NOT EXIST "%SCRIPT_DIR%Archive\processed\account_balance_history.json" (
    (
        echo {
        echo   "created": "1970-01-01T00:00:00",
        echo   "cash_accounts": {},
        echo   "credit_cards": {},
        echo   "debt_balances": {},
        echo   "totals": []
        echo }
    ) > "%SCRIPT_DIR%Archive\processed\account_balance_history.json"
    call :COLOR_INFO "Created default account_balance_history.json"
)

call :COLOR_SUCCESS "Project structure ready"

:: ========================================================
:: STEP 5: BUILD PROCESS
:: ========================================================
call :COLOR_STEP "STEP 5: Building Financial Hub"

echo Building your Financial Hub dashboard...
echo.

:: Locate build script
set "BUILD_SCRIPT=%SCRIPT_DIR%build_all.py"

if not exist "%BUILD_SCRIPT%" (
    call :COLOR_ERROR "build_all.py not found!"
    echo.
    echo Expected location: %BUILD_SCRIPT%
    echo Current directory: %CD%
    echo Script directory: %SCRIPT_DIR%
    echo.

    :: Try to find it
    call :SHOW_PROGRESS "Searching for build_all.py..."

    if exist "%CD%\build_all.py" (
        set "BUILD_SCRIPT=%CD%\build_all.py"
        call :COLOR_SUCCESS "Found at: %BUILD_SCRIPT%"
    ) else (
        call :COLOR_ERROR "Cannot locate build_all.py"
        echo.
        echo Please make sure build_all.py is in the same folder as this batch file.
        echo.
        pause
        exit /b 1
    )
)

:: Clean build option
set "DO_CLEAN_BUILD=0"
if exist "%SCRIPT_DIR%dist" (
    if exist "%SCRIPT_DIR%build" (
        echo.
        echo Previous build artifacts found.
        set /p "CLEAN_CHOICE=Clean rebuild? [Y]es or [N]o: "

        if /i "!CLEAN_CHOICE!"=="Y" set "DO_CLEAN_BUILD=1"
    )
)

if %DO_CLEAN_BUILD%==1 (
    call :SHOW_PROGRESS "Cleaning build directories..."
    if exist "%SCRIPT_DIR%build" (
        rmdir /s /q "%SCRIPT_DIR%build" 2>nul
        if !ERRORLEVEL! EQU 0 (
            call :COLOR_INFO "Cleaned: build"
        )
    )
    if exist "%SCRIPT_DIR%dist" (
        rmdir /s /q "%SCRIPT_DIR%dist" 2>nul
        if !ERRORLEVEL! EQU 0 (
            call :COLOR_INFO "Cleaned: dist"
        )
    )
)

call :SHOW_PROGRESS "Running build script..."
echo.
echo Build script: %BUILD_SCRIPT%
echo Working directory: %SCRIPT_DIR%
echo Python: %PYTHON_CMD%
echo.

:: Change to script directory
pushd "%SCRIPT_DIR%"

:: Run the build with any command line arguments passed to this script
"%PYTHON_CMD%" "%BUILD_SCRIPT%" %*

set "BUILD_EXIT_CODE=!ERRORLEVEL!"

:: Return to previous directory
popd

if %BUILD_EXIT_CODE% NEQ 0 (
    call :COLOR_ERROR "Build failed with exit code: %BUILD_EXIT_CODE%"
    goto :BUILD_FAILED
) else (
    call :COLOR_SUCCESS "Build completed!"
    goto :BUILD_SUCCESS
)

:: ========================================================
:: BUILD SUCCESS
:: ========================================================
:BUILD_SUCCESS
echo.
call :DRAW_BOX "BUILD SUCCESSFUL!"

set "FOUND_OUTPUT=0"

:: Check for HTML dashboard
if exist "%SCRIPT_DIR%financial_hub.html" (
    set "FOUND_OUTPUT=1"
    for %%F in ("%SCRIPT_DIR%financial_hub.html") do set "HTML_SIZE=%%~zF"
    set /a HTML_SIZE_KB=!HTML_SIZE! / 1024
    echo.
    call :COLOR_SUCCESS "Financial Hub Dashboard Created!"
    echo Name: financial_hub.html
    echo Location: %SCRIPT_DIR%financial_hub.html
    echo Size: !HTML_SIZE_KB! KB
    echo.
)

:: Check for reports
if exist "%SCRIPT_DIR%Archive\reports" (
    dir /b "%SCRIPT_DIR%Archive\reports\*.md" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "FOUND_OUTPUT=1"
        call :COLOR_INFO "Analysis reports in: Archive\reports\"
        echo.
    )
)

:: Check for executable builds
if exist "%SCRIPT_DIR%dist" (
    for /r "%SCRIPT_DIR%dist" %%F in (*.exe) do (
        set "FOUND_OUTPUT=1"
        for %%A in ("%%F") do set "EXE_SIZE=%%~zA"
        set /a EXE_SIZE_MB=!EXE_SIZE! / 1048576
        echo.
        call :COLOR_SUCCESS "Executable created!"
        echo Name: %%~nxF
        echo Location: %%F
        echo Size: !EXE_SIZE_MB! MB
        echo.
    )
)

if !FOUND_OUTPUT!==0 (
    call :COLOR_WARNING "No output files found"
    echo.
    echo Build completed but no output files were detected.
    echo Check the build script output above for details.
    echo.
)

:: Offer to open outputs
if exist "%SCRIPT_DIR%financial_hub.html" (
    echo.
    set /p "OPEN_HTML=Open Financial Hub dashboard in browser? (Y/N): "
    if /i "!OPEN_HTML!"=="Y" (
        echo.
        call :COLOR_INFO "Opening dashboard in your default browser..."
        start "" "%SCRIPT_DIR%financial_hub.html"
    )
)

echo.
set /p "OPEN_FOLDER=Open project folder? (Y/N): "

if /i "!OPEN_FOLDER!"=="Y" (
    echo Opening project folder...
    start "" "%SCRIPT_DIR%"
)

goto :CLEANUP

:: ========================================================
:: BUILD FAILURE
:: ========================================================
:BUILD_FAILED
echo.
call :DRAW_BOX "BUILD FAILED"
echo.
echo Build script location: %BUILD_SCRIPT%
echo Exit code: %BUILD_EXIT_CODE%
echo.
echo Check the errors above for details.
echo.
echo Log files:
echo   Main log: %LOG_FILE%
if exist "%ERROR_LOG%" echo   Error log: %ERROR_LOG%
echo.
echo Common issues:
echo   - Missing dependencies (check Step 3)
echo   - Missing data files (check Archive\raw\exports\)
echo   - Configuration file errors
echo.
pause
goto :CLEANUP

:: ========================================================
:: CLEANUP
:: ========================================================
:CLEANUP
echo.

:: Deactivate venv if active
if defined VIRTUAL_ENV (
    call deactivate 2>nul
)

echo.
call :DRAW_BOX "Thank you for using Financial Hub Builder"
call :COLOR_INFO "Session logs saved to: %LOG_FILE%"
echo.
pause
exit /b %BUILD_EXIT_CODE%