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

:: Initialize logging with safe path handling - USE TEMP IF SCRIPT DIR FAILS
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
    set "TEMP_PATH=!TEMP_PATH:~1!"
    set /a PATH_LENGTH+=1
    goto :COUNT_PATH_LENGTH
)

if !PATH_LENGTH! GTR 200 (
    call :COLOR_WARNING "Very long path detected (!PATH_LENGTH! chars)"
    call :COLOR_INFO "Windows has a 260 character limit for full file paths"
    call :COLOR_INFO "If build fails, try moving to a shorter path like C:\FinancialHub\"
    set "PATH_WARNING=1"
)

if %PATH_WARNING%==0 (
    call :COLOR_SUCCESS "Installation path is optimal"
)

:: FIXED: Check write permissions - Don't exit on failure, just warn
call :SHOW_PROGRESS "Checking write permissions..."
set "WRITE_PERMISSION_OK=1"

:: Try script directory first
echo test > "%SCRIPT_DIR%test_write.tmp" 2>nul
if %ERRORLEVEL% NEQ 0 (
    set "WRITE_PERMISSION_OK=0"
    call :COLOR_WARNING "Limited write access to script directory"
    
    :: Try TEMP directory as backup
    echo test > "%TEMP%\financial_hub_test.tmp" 2>nul
    if %ERRORLEVEL% EQU 0 (
        del "%TEMP%\financial_hub_test.tmp" 2>nul
        call :COLOR_INFO "Will use temporary directory for operations if needed"
    ) else (
        call :COLOR_ERROR "Cannot write to any directory - build may fail"
    )
) else (
    del "%SCRIPT_DIR%test_write.tmp" >nul 2>&1
    call :COLOR_SUCCESS "Write permissions OK"
)

:: CONTINUE REGARDLESS OF WRITE PERMISSIONS

goto :STEP1_PYTHON_CHECK

:: ========================================================
:: STEP 1: PYTHON DETECTION AND INSTALLATION
:: ========================================================
:STEP1_PYTHON_CHECK
call :COLOR_STEP "STEP 1: Python Environment Check"

call :SHOW_PROGRESS "Looking for Python..."

:: Test multiple Python commands
set "PYTHON_CMD="
set "PYTHON_VERSION="

:: Test python3
python3 --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=python3"
    for /f "tokens=2" %%a in ('python3 --version 2^>^&1') do set "PYTHON_VERSION=%%a"
    goto :PYTHON_FOUND
)

:: Test python
python --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=python"
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
    goto :PYTHON_FOUND
)

:: Test py launcher
py --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=py"
    for /f "tokens=2" %%a in ('py --version 2^>^&1') do set "PYTHON_VERSION=%%a"
    goto :PYTHON_FOUND
)

call :COLOR_ERROR "Python not found!"
echo.
echo Python is required to run the Financial Hub Builder.
echo.
echo Do you want to install Python automatically?
echo [Y] Yes - Download and install Python
echo [N] No  - Exit (install manually from python.org)
echo.
set /p "INSTALL_PYTHON=Your choice (Y/N): "

if /i "!INSTALL_PYTHON!"=="Y" (
    goto :INSTALL_PYTHON
) else (
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:PYTHON_FOUND
call :COLOR_SUCCESS "Found Python %PYTHON_VERSION% (%PYTHON_CMD%)"

:: Check Python version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)

if %PY_MAJOR% LSS 3 (
    call :COLOR_ERROR "Python version too old: %PYTHON_VERSION%"
    call :COLOR_INFO "Python 3.8 or newer is required"
    goto :INSTALL_PYTHON
) else if %PY_MAJOR% EQU 3 if %PY_MINOR% LSS 8 (
    call :COLOR_ERROR "Python version too old: %PYTHON_VERSION%"
    call :COLOR_INFO "Python 3.8 or newer is required"
    goto :INSTALL_PYTHON
) else (
    call :COLOR_SUCCESS "Python version is compatible"
)

goto :STEP2_DEPENDENCIES

:INSTALL_PYTHON
call :SHOW_PROGRESS "Installing Python..."
call :COLOR_WARNING "Python installation feature coming soon"
echo.
echo Please install Python manually:
echo 1. Go to https://python.org/downloads/
echo 2. Download Python 3.11 or newer
echo 3. Run installer and CHECK "Add Python to PATH"
echo 4. Restart this script
echo.
pause
exit /b 1

:: ========================================================
:: STEP 2: DEPENDENCY CHECK
:: ========================================================
:STEP2_DEPENDENCIES
call :COLOR_STEP "STEP 2: Checking Dependencies"

call :SHOW_PROGRESS "Testing pip package manager..."
%PYTHON_CMD% -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :COLOR_ERROR "pip not available"
    echo.
    echo pip is required to install Python packages.
    echo Try reinstalling Python and ensure pip is included.
    pause
    exit /b 1
) else (
    call :COLOR_SUCCESS "pip is available"
)

:: Check for required packages
call :SHOW_PROGRESS "Checking required packages..."
set "MISSING_PACKAGES="

:: Test each package
for %%p in (pandas openpyxl pathlib datetime collections) do (
    %PYTHON_CMD% -c "import %%p" >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        set "MISSING_PACKAGES=!MISSING_PACKAGES! %%p"
    )
)

if defined MISSING_PACKAGES (
    call :COLOR_WARNING "Missing packages:%MISSING_PACKAGES%"
    echo.
    echo Installing required packages...
    %PYTHON_CMD% -m pip install pandas openpyxl --break-system-packages 2>nul
    if !ERRORLEVEL! NEQ 0 (
        %PYTHON_CMD% -m pip install pandas openpyxl
    )
    
    if !ERRORLEVEL! NEQ 0 (
        call :COLOR_ERROR "Failed to install packages"
        echo.
        echo Try running as administrator or install manually:
        echo   pip install pandas openpyxl
        pause
        exit /b 1
    ) else (
        call :COLOR_SUCCESS "Packages installed successfully"
    )
) else (
    call :COLOR_SUCCESS "All required packages are available"
)

:: ========================================================
:: STEP 3: PROJECT STRUCTURE
:: ========================================================
call :COLOR_STEP "STEP 3: Setting Up Project Structure"

call :SHOW_PROGRESS "Creating directories..."

:: Create Archive structure
if not exist "%SCRIPT_DIR%Archive" mkdir "%SCRIPT_DIR%Archive"
if not exist "%SCRIPT_DIR%Archive\raw" mkdir "%SCRIPT_DIR%Archive\raw"
if not exist "%SCRIPT_DIR%Archive\raw\exports" mkdir "%SCRIPT_DIR%Archive\raw\exports"
if not exist "%SCRIPT_DIR%Archive\processed" mkdir "%SCRIPT_DIR%Archive\processed"
if not exist "%SCRIPT_DIR%Archive\reports" mkdir "%SCRIPT_DIR%Archive\reports"

call :COLOR_SUCCESS "Directory structure created"

:: Create default config files if they don't exist
call :SHOW_PROGRESS "Creating default configuration files..."

IF NOT EXIST "%SCRIPT_DIR%Archive\processed\financial_config.json" (
    (
        echo {
        echo   "recurring_expenses": {},
        echo   "account_mapping": {},
        echo   "category_mapping": {},
        echo   "metadata": {"last_updated": "1970-01-01"}
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

IF NOT EXIST "%SCRIPT_DIR%Archive\raw\exports\AllTransactions.csv" (
    echo Date,Name,Amount,Category,Account Name,Description,Custom Name,Ignored From > "%SCRIPT_DIR%Archive\raw\exports\AllTransactions.csv"
    call :COLOR_INFO "Created default AllTransactions.csv"
)

call :COLOR_SUCCESS "Project structure ready"

:: ========================================================
:: STEP 4: BUILD PROCESS
:: ========================================================
call :COLOR_STEP "STEP 4: Building Financial Hub"

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
echo   - Missing dependencies (check Step 2)
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