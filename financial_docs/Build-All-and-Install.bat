@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ========================================================
:: ENTERPRISE BUILD SYSTEM v2.0 - FINAL VERSION
:: One-Stop Shop for Non-Technical Users
:: ========================================================

:: Detect if running in PowerShell
set "IN_POWERSHELL=0"
echo %PSModulePath% | find "PowerShell" >nul 2>&1
if %ERRORLEVEL%==0 set "IN_POWERSHELL=1"

:: Initialize logging
set "LOG_DIR=logs"
set "TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "LOG_FILE=%LOG_DIR%\build_%TIMESTAMP%.log"
set "ERROR_LOG=%LOG_DIR%\errors_%TIMESTAMP%.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ========================================================>> "%LOG_FILE%"
echo BUILD SYSTEM STARTED: %date% %time% >> "%LOG_FILE%"
echo ========================================================>> "%LOG_FILE%"

goto :MAIN

:: ========================================================
:: COLOR HELPER FUNCTIONS
:: ========================================================

:COLOR_SUCCESS
    if %IN_POWERSHELL%==1 (
        powershell -Command "Write-Host '[SUCCESS]' -ForegroundColor Green -NoNewline; Write-Host ' %~1'"
    ) else (
        echo [SUCCESS] %~1
    )
    echo [SUCCESS] %~1 >> "%LOG_FILE%"
    exit /b

:COLOR_INFO
    if %IN_POWERSHELL%==1 (
        powershell -Command "Write-Host '[INFO]' -ForegroundColor Cyan -NoNewline; Write-Host ' %~1'"
    ) else (
        echo [INFO] %~1
    )
    echo [INFO] %~1 >> "%LOG_FILE%" 2>nul
    exit /b

:COLOR_WARNING
    if %IN_POWERSHELL%==1 (
        powershell -Command "Write-Host '[WARNING]' -ForegroundColor Yellow -NoNewline; Write-Host ' %~1'"
    ) else (
        echo [WARNING] %~1
    )
    echo [WARNING] %~1 >> "%LOG_FILE%"
    echo [WARNING] %~1 >> "%ERROR_LOG%"
    exit /b

:COLOR_ERROR
    if %IN_POWERSHELL%==1 (
        powershell -Command "Write-Host '[ERROR]' -ForegroundColor Red -NoNewline; Write-Host ' %~1'"
    ) else (
        echo [ERROR] %~1
    )
    echo [ERROR] %~1 >> "%LOG_FILE%"
    echo [ERROR] %~1 >> "%ERROR_LOG%"
    exit /b

:COLOR_STEP
    echo.
    if %IN_POWERSHELL%==1 (
        powershell -Command "Write-Host '========================================' -ForegroundColor Magenta"
        powershell -Command "Write-Host ' %~1' -ForegroundColor Magenta"
        powershell -Command "Write-Host '========================================' -ForegroundColor Magenta"
    ) else (
        echo ========================================
        echo  %~1
        echo ========================================
    )
    echo.
    echo ======================================== >> "%LOG_FILE%"
    echo  %~1 >> "%LOG_FILE%"
    echo ======================================== >> "%LOG_FILE%"
    exit /b

:SHOW_PROGRESS
    if %IN_POWERSHELL%==1 (
        powershell -Command "Write-Host '[PROGRESS]' -ForegroundColor Blue -NoNewline; Write-Host ' %~1'"
    ) else (
        echo [PROGRESS] %~1
    )
    echo [PROGRESS] %~1 >> "%LOG_FILE%"
    exit /b

:COUNTDOWN
    set /a seconds=%~1
    echo.
    call :COLOR_INFO "Waiting %seconds% seconds..."
    for /l %%i in (%seconds%,-1,1) do (
        <nul set /p "=%%i... "
        ping 127.0.0.1 -n 2 >nul
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
call :DRAW_BOX "WELCOME TO THE BUILD SYSTEM v2.0"

if %IN_POWERSHELL%==1 (
    powershell -Command "Write-Host 'This tool will automatically:' -ForegroundColor Green"
    powershell -Command "Write-Host '  * Check your computer is ready' -ForegroundColor White"
    powershell -Command "Write-Host '  * Install any missing software' -ForegroundColor White"
    powershell -Command "Write-Host '  * Set up your project environment' -ForegroundColor White"
    powershell -Command "Write-Host '  * Build your application' -ForegroundColor White"
    echo.
    powershell -Command "Write-Host 'No technical knowledge required!' -ForegroundColor Yellow"
) else (
    echo This tool will automatically:
    echo   * Check your computer is ready
    echo   * Install any missing software
    echo   * Set up your project environment
    echo   * Build your application
    echo.
    echo No technical knowledge required!
)

echo Just sit back and let the system do the work.
echo.
pause

call :COLOR_STEP "SYSTEM INFORMATION"
call :COLOR_INFO "Operating System: %OS%"
call :COLOR_INFO "Computer Name: %COMPUTERNAME%"
call :COLOR_INFO "User: %USERNAME%"
call :COLOR_INFO "Script Location: %~dp0"

:: ========================================================
:: STEP 0: PRE-FLIGHT CHECKS
:: ========================================================
call :COLOR_STEP "STEP 0: Pre-Flight Checks"

call :SHOW_PROGRESS "Checking administrator privileges..."
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
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
        pause
        powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
        exit /b 0
    ) else (
        call :COLOR_INFO "Continuing without administrator privileges"
    )
) else (
    call :COLOR_SUCCESS "Administrator privileges confirmed"
)

call :SHOW_PROGRESS "Checking installation path..."
echo "%~dp0" | findstr " " >nul 2>&1
if %ERRORLEVEL% == 0 (
    call :COLOR_ERROR "The installation path contains spaces!"
    call :DRAW_BOX "PATH ERROR DETECTED"
    echo The current folder path has spaces in it:
    echo "%~dp0"
    echo.
    echo How to fix:
    echo 1. Close this window
    echo 2. Move this entire folder to: C:\ProjectName
    echo 3. Run this script again from the new location
    echo.
    echo Spaces in paths can cause installation problems!
    echo.
    pause
    exit /b 1
)
call :COLOR_SUCCESS "Installation path is valid"

call :SHOW_PROGRESS "Checking available disk space..."
for /f "tokens=3" %%a in ('dir /-c "%~dp0" 2^>nul ^| find "bytes free"') do set FREE_SPACE=%%a
set FREE_SPACE=%FREE_SPACE:,=%
if defined FREE_SPACE (
    set /a FREE_SPACE_GB=%FREE_SPACE:~0,-9%
    if !FREE_SPACE_GB! LSS 1 (
        call :COLOR_WARNING "Low disk space: !FREE_SPACE_GB! GB available"
        echo The build may fail if space runs out
    ) else (
        call :COLOR_SUCCESS "Disk space OK: !FREE_SPACE_GB! GB available"
    )
) else (
    call :COLOR_WARNING "Could not determine disk space"
)

call :SHOW_PROGRESS "Checking internet connection..."
ping -n 1 8.8.8.8 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :COLOR_ERROR "No internet connection detected!"
    call :DRAW_BOX "NO INTERNET CONNECTION FOUND"
    echo This tool needs internet access to download components.
    echo.
    echo Please:
    echo 1. Check your internet connection
    echo 2. Make sure WiFi is enabled
    echo 3. Try running this script again
    echo.
    pause
    exit /b 1
) else (
    call :COLOR_SUCCESS "Internet connection confirmed"
)

echo.
call :COLOR_SUCCESS "All pre-flight checks passed!"
echo.

:: ========================================================
:: STEP 1: PYTHON INSTALLATION & VERIFICATION
:: ========================================================
call :COLOR_STEP "STEP 1: Python Environment Setup"

call :SHOW_PROGRESS "Looking for Python on your computer..."

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    call :COLOR_WARNING "Python not found on this system"
    echo.
    echo Python is not installed on your computer yet.
    echo.
    
    :: Try Microsoft Store Python first
    call :SHOW_PROGRESS "Checking for Microsoft Store..."
    where winget >nul 2>&1
    if %ERRORLEVEL% == 0 (
        call :COLOR_INFO "Attempting to install Python from Microsoft Store..."
        echo This is the easiest and most reliable method.
        echo.
        
        winget install --id 9NCVDN91XZQP --source msstore --accept-package-agreements --accept-source-agreements
        
        if !ERRORLEVEL! == 0 (
            call :COLOR_SUCCESS "Python installed from Microsoft Store!"
            echo.
            echo NEXT STEP: Close this window and run the script again
            echo.
            pause
            exit /b 0
        )
    )
    
    :: Fallback: Direct download
    call :COLOR_INFO "Downloading Python installer..."
    echo.
    
    set "PYTHON_INSTALLER=python-3.12.7-amd64.exe"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
    
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
    
    if exist "%PYTHON_INSTALLER%" (
        call :COLOR_SUCCESS "Download complete!"
        echo.
        echo Opening Python installer...
        echo.
        echo IMPORTANT: When the installer opens:
        echo   1. CHECK the box that says "Add Python to PATH"
        echo   2. Click "Install Now"
        echo.
        pause
        
        start /wait "" "%PYTHON_INSTALLER%"
        del "%PYTHON_INSTALLER%" >nul 2>&1
        
        call :COLOR_SUCCESS "Installation complete!"
        echo.
        echo NEXT STEP: Close this window and run the script again
        echo.
        pause
        exit /b 0
    ) else (
        call :COLOR_ERROR "Could not download Python"
        echo.
        echo Please install Python manually:
        echo 1. Visit: https://www.python.org/downloads/
        echo 2. Download Python 3.12
        echo 3. Run the installer (check "Add Python to PATH")
        echo 4. Run this script again
        echo.
        pause
        exit /b 1
    )
    
) ELSE (
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
    call :COLOR_SUCCESS "Python is already installed (version %PYTHON_VERSION%)"
)

:: ========================================================
:: STEP 2: VIRTUAL ENVIRONMENT SETUP
:: ========================================================
call :COLOR_STEP "STEP 2: Setting Up Isolated Environment"

echo Creating a clean workspace for your project...
echo.

IF NOT EXIST "venv" (
    call :SHOW_PROGRESS "Creating virtual environment..."
    python -m venv venv
    
    if %ERRORLEVEL% NEQ 0 (
        call :COLOR_ERROR "Failed to create virtual environment"
        pause
        exit /b 1
    )
    
    call :COLOR_SUCCESS "Virtual environment created"
) ELSE (
    call :COLOR_INFO "Virtual environment already exists"
)

call :SHOW_PROGRESS "Activating virtual environment..."
call venv\Scripts\activate

if %ERRORLEVEL% NEQ 0 (
    call :COLOR_ERROR "Failed to activate virtual environment"
    pause
    exit /b 1
)

call :COLOR_SUCCESS "Virtual environment activated"

:: ========================================================
:: STEP 3: DEPENDENCY INSTALLATION
:: ========================================================
call :COLOR_STEP "STEP 3: Installing Required Components"

echo Installing project dependencies...
echo.

set "MAX_RETRIES=3"
set "RETRY_COUNT=0"

:INSTALL_DEPENDENCIES
set /a RETRY_COUNT+=1

IF EXIST "requirements.txt" (
    call :SHOW_PROGRESS "Installing components (Attempt %RETRY_COUNT%/%MAX_RETRIES%)..."
    
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt
    
    if %ERRORLEVEL% NEQ 0 (
        call :COLOR_ERROR "Installation failed (Attempt %RETRY_COUNT%)"
        
        if %RETRY_COUNT% LSS %MAX_RETRIES% (
            echo Retrying in 5 seconds...
            call :COUNTDOWN 5
            goto :INSTALL_DEPENDENCIES
        ) else (
            call :COLOR_ERROR "Failed after 3 attempts"
            pause
            exit /b 1
        )
    )
    
    call :COLOR_SUCCESS "All components installed"
    
) ELSE (
    call :COLOR_WARNING "requirements.txt not found"
    pip install pyinstaller
    call :COLOR_SUCCESS "PyInstaller installed"
)

:: ========================================================
:: STEP 4: PROJECT STRUCTURE
:: ========================================================
call :COLOR_STEP "STEP 4: Preparing Project Structure"

call :SHOW_PROGRESS "Creating directories..."
if not exist "Archive\reports" mkdir "Archive\reports" >nul 2>&1
if not exist "Archive\processed" mkdir "Archive\processed" >nul 2>&1
if not exist "Archive\raw\exports" mkdir "Archive\raw\exports" >nul 2>&1

call :SHOW_PROGRESS "Initializing config files..."

IF NOT EXIST "Archive\processed\financial_config.json" (
    (
        echo {
        echo   "metadata": {"last_updated": "1970-01-01", "version": "2.0"},
        echo   "cash_accounts": {},
        echo   "credit_cards": {},
        echo   "debt_balances": {},
        echo   "recurring_expenses": {}
        echo }
    ) > "Archive\processed\financial_config.json"
)

IF NOT EXIST "Archive\processed\budget.json" (
    (
        echo {
        echo   "metadata": {"total_spending_budget": 5000, "last_updated": "1970-01-01"},
        echo   "monthly_income": {"earnings": 7500},
        echo   "category_budgets": {}
        echo }
    ) > "Archive\processed\budget.json"
)

IF NOT EXIST "Archive\processed\financial_goals.json" (
    (
        echo {
        echo   "goals": {},
        echo   "metadata": {"last_updated": "1970-01-01"}
        echo }
    ) > "Archive\processed\financial_goals.json"
)

IF NOT EXIST "Archive\raw\exports\AllTransactions.csv" (
    echo Date,Name,Amount,Category,Account Name,Description,Custom Name,Ignored From > "Archive\raw\exports\AllTransactions.csv"
)

IF NOT EXIST "Archive\processed\account_balance_history.json" (
    (
        echo {
        echo   "created": "1970-01-01T00:00:00",
        echo   "cash_accounts": {},
        echo   "credit_cards": {},
        echo   "debt_balances": {},
        echo   "totals": []
        echo }
    ) > "Archive\processed\account_balance_history.json"
)

call :COLOR_SUCCESS "Project structure ready"

:: ========================================================
:: STEP 5: BUILD PROCESS
:: ========================================================
call :COLOR_STEP "STEP 5: Building Application"

echo Building your application...
echo.

:: Store the script directory
set "SCRIPT_DIR=%~dp0"
set "BUILD_SCRIPT=%SCRIPT_DIR%build_all.py"

:: Check if build_all.py exists
if not exist "%BUILD_SCRIPT%" (
    call :COLOR_ERROR "build_all.py not found!"
    echo.
    echo Expected location: %BUILD_SCRIPT%
    echo.
    echo Please make sure build_all.py is in the same folder as this batch file.
    echo.
    pause
    exit /b 1
)

set "DO_CLEAN_BUILD=1"
if exist "%SCRIPT_DIR%dist" (
    if exist "%SCRIPT_DIR%build" (
        echo Previous build found. Clean rebuild?
        set /p "CLEAN_CHOICE=[Y]es or [N]o: "
        
        if /i "!CLEAN_CHOICE!"=="N" set "DO_CLEAN_BUILD=0"
    )
)

if %DO_CLEAN_BUILD%==1 (
    call :SHOW_PROGRESS "Cleaning build directories..."
    if exist "%SCRIPT_DIR%build" rmdir /s /q "%SCRIPT_DIR%build" 2>nul
    if exist "%SCRIPT_DIR%dist" rmdir /s /q "%SCRIPT_DIR%dist" 2>nul
)

call :SHOW_PROGRESS "Running build script..."
echo.
echo Build script: %BUILD_SCRIPT%
echo Working directory: %SCRIPT_DIR%
echo.

:: Change to script directory before running build
pushd "%SCRIPT_DIR%"

python "%BUILD_SCRIPT%" %*

set "BUILD_EXIT_CODE=%ERRORLEVEL%"

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

set "SCRIPT_DIR=%~dp0"
set "FOUND_OUTPUT=0"

:: Check for executable builds
if exist "%SCRIPT_DIR%dist" (
    for /r "%SCRIPT_DIR%dist" %%F in (*.exe) do (
        set "FOUND_OUTPUT=1"
        echo.
        call :COLOR_SUCCESS "Executable created!"
        echo Name: %%~nxF
        echo Location: %%F
        echo.
    )
)

:: Check for HTML builds
if exist "%SCRIPT_DIR%financial_hub.html" (
    set "FOUND_OUTPUT=1"
    for %%F in ("%SCRIPT_DIR%financial_hub.html") do set "HTML_SIZE=%%~zF"
    set /a HTML_SIZE_KB=!HTML_SIZE! / 1024
    echo.
    call :COLOR_SUCCESS "Financial Hub created!"
    echo Name: financial_hub.html
    echo Location: %SCRIPT_DIR%financial_hub.html
    echo Size: !HTML_SIZE_KB! KB
    echo.
)

:: Check for reports
if exist "%SCRIPT_DIR%Archive\reports" (
    echo Additional reports in: %SCRIPT_DIR%Archive\reports\
    echo.
)

if !FOUND_OUTPUT!==0 (
    call :COLOR_WARNING "No output files found"
    echo.
)

set /p "OPEN_FOLDER=Open project folder? (Y/N): "

if /i "!OPEN_FOLDER!"=="Y" (
    echo Opening project folder...
    start "" "%SCRIPT_DIR%"
)

:: Offer to open HTML file directly
if exist "%SCRIPT_DIR%financial_hub.html" (
    echo.
    set /p "OPEN_HTML=Open financial_hub.html in browser? (Y/N): "
    if /i "!OPEN_HTML!"=="Y" (
        start "" "%SCRIPT_DIR%financial_hub.html"
    )
)

goto :CLEANUP

:: ========================================================
:: BUILD FAILURE
:: ========================================================
:BUILD_FAILED
echo.
call :DRAW_BOX "BUILD FAILED"
echo.
echo Build script location: %~dp0
echo Check the errors above for details.
echo.
echo Log file: %LOG_FILE%
if exist "%ERROR_LOG%" echo Error log: %ERROR_LOG%
echo.
pause
goto :CLEANUP

:: ========================================================
:: CLEANUP
:: ========================================================
:CLEANUP
echo.
call deactivate 2>nul
echo.
call :DRAW_BOX "Thank you for using Build System v2.0"
echo.
pause
exit /b 0