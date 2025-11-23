@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ========================================================
:: ENTERPRISE BUILD SYSTEM v2.0 - COMPLETE VERSION
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
    echo [INFO] %~1 >> "%LOG_FILE%"
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
call :DRAW_BOX "Press any key to begin..."
pause >nul

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
    call :COLOR_WARNING "Administrator privileges required!"
    echo.
    echo This program needs administrator access to install software.
    echo The window will close and reopen with the right permissions.
    echo.
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
call :COLOR_SUCCESS "Administrator privileges confirmed"

call :SHOW_PROGRESS "Checking installation path..."
echo "%~dp0" | findstr /c:" " >nul 2>&1
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
    exit /b
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
    exit /b
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
    echo Don't worry! We'll try to install it for you.
    echo.
    
    :: Check for winget
    call :SHOW_PROGRESS "Checking for Windows Package Manager (winget)..."
    winget --version >nul 2>&1
    if %ERRORLEVEL% == 0 (
        call :COLOR_INFO "Found winget! Attempting installation..."
        echo.
        
        :: Try winget with output visible
        winget install -e --id Python.Python.3.12
        
        set "WINGET_EXIT=!ERRORLEVEL!"
        echo.
        call :COLOR_INFO "Winget exit code: !WINGET_EXIT!"
        
        if !WINGET_EXIT! == 0 (
            call :COLOR_SUCCESS "Python installed successfully via winget!"
            echo.
            echo Python has been installed!
            echo Please close this window and run the script again.
            echo This allows Windows to recognize the new Python installation.
            echo.
            call :COUNTDOWN 5
            exit /b
        ) else (
            call :COLOR_WARNING "Winget installation failed with code: !WINGET_EXIT!"
        )
    ) else (
        call :COLOR_WARNING "Winget not found on this system"
    )
    
    echo.
    :: Check for Chocolatey
    call :SHOW_PROGRESS "Checking for Chocolatey package manager..."
    choco --version >nul 2>&1
    if %ERRORLEVEL% == 0 (
        call :COLOR_INFO "Found Chocolatey! Attempting installation..."
        echo.
        
        choco install python312 -y
        
        set "CHOCO_EXIT=!ERRORLEVEL!"
        echo.
        call :COLOR_INFO "Chocolatey exit code: !CHOCO_EXIT!"
        
        if !CHOCO_EXIT! == 0 (
            call :COLOR_SUCCESS "Python installed successfully via Chocolatey!"
            echo.
            echo Python has been installed!
            echo Please close this window and run the script again.
            echo This allows Windows to recognize the new Python installation.
            echo.
            call :COUNTDOWN 5
            exit /b
        ) else (
            call :COLOR_WARNING "Chocolatey installation failed with code: !CHOCO_EXIT!"
        )
    ) else (
        call :COLOR_WARNING "Chocolatey not found on this system"
    )
    
    echo.
    :: Direct download method
    call :COLOR_INFO "Attempting direct download from python.org..."
    echo.
    
    set "PYTHON_INSTALLER=python-3.12.7-amd64.exe"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
    
    call :SHOW_PROGRESS "Downloading Python installer..."
    echo Downloading from: %PYTHON_URL%
    echo.
    
    :: Use PowerShell with error handling
    powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Starting download...'; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -ErrorAction Stop; Write-Host 'Download complete!'; exit 0 } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 }"
    
    set "DOWNLOAD_EXIT=!ERRORLEVEL!"
    
    if !DOWNLOAD_EXIT! NEQ 0 (
        call :COLOR_ERROR "Download failed with exit code: !DOWNLOAD_EXIT!"
        goto :MANUAL_INSTALL
    )
    
    if not exist "%PYTHON_INSTALLER%" (
        call :COLOR_ERROR "Installer file not found after download"
        goto :MANUAL_INSTALL
    )
    
    :: Check file size to ensure it downloaded properly
    for %%A in ("%PYTHON_INSTALLER%") do set "INSTALLER_SIZE=%%~zA"
    if !INSTALLER_SIZE! LSS 1000000 (
        call :COLOR_ERROR "Downloaded file is too small (!INSTALLER_SIZE! bytes)"
        del "%PYTHON_INSTALLER%" >nul 2>&1
        goto :MANUAL_INSTALL
    )
    
    call :COLOR_SUCCESS "Download complete! (Size: !INSTALLER_SIZE! bytes)"
    echo.
    
    :: Offer interactive or silent installation
    echo Python installer is ready.
    echo.
    echo Choose installation method:
    echo [A] Automatic (silent) - faster, no interaction needed
    echo [I] Interactive - you can see and control the installation
    echo [M] Manual - open installer and exit this script
    echo.
    set /p "INSTALL_METHOD=Your choice (A/I/M): "
    
    if /i "!INSTALL_METHOD!"=="M" (
        call :COLOR_INFO "Opening installer for manual installation..."
        start "" "%PYTHON_INSTALLER%"
        echo.
        echo Please complete the installation manually.
        echo IMPORTANT: Make sure to check "Add Python to PATH"
        echo.
        echo After installation completes, run this script again.
        echo.
        pause
        exit /b
    )
    
    if /i "!INSTALL_METHOD!"=="I" (
        call :COLOR_INFO "Starting interactive installation..."
        echo.
        echo IMPORTANT: When the installer opens, make sure to:
        echo   1. Check "Add Python to PATH" at the bottom
        echo   2. Click "Install Now"
        echo.
        pause
        
        start /wait "" "%PYTHON_INSTALLER%"
        
        set "INSTALL_EXIT=!ERRORLEVEL!"
    ) else (
        call :COLOR_INFO "Starting automatic installation..."
        call :SHOW_PROGRESS "Installing Python silently (this may take 2-3 minutes)..."
        echo.
        
        :: Try silent installation with detailed logging
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 /log "%LOG_DIR%\python_install.log"
        
        set "INSTALL_EXIT=!ERRORLEVEL!"
        
        echo.
        call :COLOR_INFO "Installation exit code: !INSTALL_EXIT!"
        
        :: Show installation log if it exists
        if exist "%LOG_DIR%\python_install.log" (
            echo.
            echo Installation log saved to: %LOG_DIR%\python_install.log
            echo Last 10 lines of installation log:
            echo ----------------------------------------
            powershell -Command "Get-Content '%LOG_DIR%\python_install.log' -Tail 10"
            echo ----------------------------------------
        )
    )
    
    :: Clean up installer
    if exist "%PYTHON_INSTALLER%" (
        call :COLOR_INFO "Cleaning up installer file..."
        del "%PYTHON_INSTALLER%" >nul 2>&1
    )
    
    if !INSTALL_EXIT! == 0 (
        call :COLOR_SUCCESS "Python installation completed!"
        echo.
        echo Python has been installed!
        echo Please close this window and run the script again.
        echo This allows Windows to recognize the new Python installation.
        echo.
        call :COUNTDOWN 5
        exit /b
    ) else (
        call :COLOR_ERROR "Installation failed with exit code: !INSTALL_EXIT!"
        if exist "%LOG_DIR%\python_install.log" (
            echo Check the installation log for details: %LOG_DIR%\python_install.log
        )
        goto :MANUAL_INSTALL
    )
    
    :MANUAL_INSTALL
    call :COLOR_ERROR "All automatic installation methods failed"
    call :DRAW_BOX "MANUAL INSTALLATION REQUIRED"
    echo.
    echo Please install Python manually:
    echo.
    echo Option 1 - Direct Download:
    echo   1. Visit: https://www.python.org/downloads/
    echo   2. Click "Download Python 3.12"
    echo   3. Run the installer
    echo   4. CRITICAL: Check "Add Python to PATH" checkbox
    echo   5. Click "Install Now"
    echo   6. Run this script again
    echo.
    echo Option 2 - Microsoft Store (Easiest):
    echo   1. Open Microsoft Store
    echo   2. Search for "Python 3.12"
    echo   3. Click "Get" or "Install"
    echo   4. Run this script again
    echo.
    echo Option 3 - Install Winget first (Recommended for future):
    echo   1. Install "App Installer" from Microsoft Store
    echo   2. Run this script again
    echo.
    
    set /p "OPEN_BROWSER=Open Python download page in browser? (Y/N): "
    if /i "!OPEN_BROWSER!"=="Y" (
        start https://www.python.org/downloads/
    )
    
    pause
    exit /b
    
) ELSE (
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
    call :COLOR_SUCCESS "Python is already installed (version %PYTHON_VERSION%)"
)

:: ========================================================
:: STEP 2: VIRTUAL ENVIRONMENT SETUP
:: ========================================================
call :COLOR_STEP "STEP 2: Setting Up Isolated Environment"

echo Creating a clean, isolated workspace for your project...
echo This keeps everything organized and prevents conflicts.
echo.

IF NOT EXIST "venv" (
    call :SHOW_PROGRESS "Creating virtual environment..."
    python -m venv venv
    
    if %ERRORLEVEL% NEQ 0 (
        call :COLOR_ERROR "Failed to create virtual environment"
        echo Could not create virtual environment.
        echo This might mean Python is not properly installed.
        pause
        exit /b
    )
    
    call :COLOR_SUCCESS "Virtual environment created"
) ELSE (
    call :COLOR_INFO "Virtual environment already exists"
)

call :SHOW_PROGRESS "Activating virtual environment..."
call venv\Scripts\activate

if %ERRORLEVEL% NEQ 0 (
    call :COLOR_ERROR "Failed to activate virtual environment"
    echo Could not activate the virtual environment.
    pause
    exit /b
)

call :COLOR_SUCCESS "Virtual environment activated"

:: ========================================================
:: STEP 3: DEPENDENCY INSTALLATION WITH RETRY LOGIC
:: ========================================================
call :COLOR_STEP "STEP 3: Installing Required Software Components"

echo Installing all the tools your project needs...
echo.

set "MAX_RETRIES=3"
set "RETRY_COUNT=0"

:INSTALL_DEPENDENCIES
set /a RETRY_COUNT+=1

IF EXIST "requirements.txt" (
    call :SHOW_PROGRESS "Installing components (Attempt %RETRY_COUNT%/%MAX_RETRIES%)..."
    echo.
    
    call :COLOR_INFO "Upgrading pip to latest version..."
    python -m pip install --upgrade pip --quiet
    
    python -m pip install -r requirements.txt
    
    if %ERRORLEVEL% NEQ 0 (
        call :COLOR_ERROR "Dependency installation failed (Attempt %RETRY_COUNT%)"
        
        if %RETRY_COUNT% LSS %MAX_RETRIES% (
            echo.
            echo Installation encountered an error.
            echo Retrying in 5 seconds... (Attempt %RETRY_COUNT% of %MAX_RETRIES%)
            call :COUNTDOWN 5
            goto :INSTALL_DEPENDENCIES
        ) else (
            call :DRAW_BOX "COMPONENT INSTALLATION FAILED"
            echo After 3 attempts, we couldn't install all components.
            echo.
            echo Troubleshooting steps:
            echo 1. Check your internet connection
            echo 2. Temporarily disable antivirus/firewall
            echo 3. Try running as a different user
            echo 4. Check if you're behind a corporate proxy
            echo.
            echo Error details saved to: %ERROR_LOG%
            echo.
            pause
            exit /b
        )
    )
    
    call :COLOR_SUCCESS "All components installed successfully"
    
) ELSE (
    call :COLOR_WARNING "requirements.txt not found"
    echo Installing PyInstaller as fallback...
    
    pip show pyinstaller >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        call :SHOW_PROGRESS "Installing PyInstaller..."
        pip install pyinstaller
        
        if %ERRORLEVEL% NEQ 0 (
            call :COLOR_ERROR "Failed to install PyInstaller"
            pause
            exit /b
        )
    )
    call :COLOR_SUCCESS "PyInstaller ready"
)

call :SHOW_PROGRESS "Verifying installations..."
pip list >> "%LOG_FILE%"
call :COLOR_SUCCESS "Component verification complete"

:: ========================================================
:: STEP 4: PROJECT STRUCTURE INITIALIZATION
:: ========================================================
call :COLOR_STEP "STEP 4: Preparing Project Structure"

echo Setting up your project folders and files...
echo.

call :SHOW_PROGRESS "Creating Archive directories..."
if not exist "Archive\reports" mkdir "Archive\reports" >nul 2>&1
if not exist "Archive\processed" mkdir "Archive\processed" >nul 2>&1
if not exist "Archive\raw\exports" mkdir "Archive\raw\exports" >nul 2>&1

call :COLOR_SUCCESS "Archive directories created"

call :SHOW_PROGRESS "Initializing configuration files..."

IF NOT EXIST "Archive\processed\financial_config.json" (
    (
        echo {
        echo   "metadata": {
        echo     "last_updated": "1970-01-01",
        echo     "version": "2.0"
        echo   },
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
        echo   "metadata": {
        echo     "total_spending_budget": 5000,
        echo     "last_updated": "1970-01-01"
        echo   },
        echo   "monthly_income": {
        echo     "earnings": 7500
        echo   },
        echo   "category_budgets": {}
        echo }
    ) > "Archive\processed\budget.json"
)

IF NOT EXIST "Archive\processed\financial_goals.json" (
    (
        echo {
        echo   "goals": {},
        echo   "metadata": {
        echo     "last_updated": "1970-01-01"
        echo   }
        echo }
    ) > "Archive\processed\financial_goals.json"
)

IF NOT EXIST "Archive\raw\exports\AllTransactions.csv" (
    (
        echo Date,Name,Amount,Category,Account Name,Description,Custom Name,Ignored From
    ) > "Archive\raw\exports\AllTransactions.csv"
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

call :COLOR_SUCCESS "Configuration files initialized"

call :SHOW_PROGRESS "Validating project structure..."
if not exist "Archive\processed\financial_config.json" (
    call :COLOR_WARNING "Some files could not be created"
) else (
    call :COLOR_SUCCESS "All critical files validated"
)

:: ========================================================
:: STEP 5: BUILD PROCESS
:: ========================================================
call :COLOR_STEP "STEP 5: Building Your Application"

echo Now we're building your application into an executable file...
echo This is where your code becomes a program you can run!
echo.

set "DO_CLEAN_BUILD=1"
if exist "dist" (
    if exist "build" (
        call :COLOR_INFO "Previous build files found"
        echo.
        echo Do you want to do a clean build?
        echo [Y] Yes - Clean everything and rebuild (safer, slower)
        echo [N] No  - Keep existing files (faster, may have issues)
        echo.
        set /p "CLEAN_CHOICE=Your choice (Y/N): "
        
        if /i "!CLEAN_CHOICE!"=="N" (
            set "DO_CLEAN_BUILD=0"
        )
    )
)

if %DO_CLEAN_BUILD%==1 (
    call :SHOW_PROGRESS "Cleaning previous build files..."
    
    if exist "dist" (
        set "BACKUP_DIR=dist_backup_!TIMESTAMP!"
        echo Creating backup: !BACKUP_DIR!
        move "dist" "!BACKUP_DIR!" >nul 2>&1
    )
    
    if exist "build" rmdir /s /q "build" 2>nul
    if exist "dist" rmdir /s /q "dist" 2>nul
    
    call :COLOR_SUCCESS "Build directories cleaned"
)

echo.
call :SHOW_PROGRESS "Running build_all.py..."
echo This may take several minutes. Please be patient...
echo.

python build_all.py %*

set "BUILD_EXIT_CODE=%ERRORLEVEL%"

if %BUILD_EXIT_CODE% NEQ 0 (
    call :COLOR_ERROR "Build process failed"
    call :DRAW_BOX "BUILD FAILED"
    echo The build process encountered an error.
    echo.
    echo What you can try:
    echo 1. Check the error messages above
    echo 2. Look at the log file: %LOG_FILE%
    echo 3. Try running the build again
    echo 4. Make sure build_all.py exists in this folder
    echo.
    goto :BUILD_FAILED
) else (
    call :COLOR_SUCCESS "Build completed successfully!"
    goto :BUILD_SUCCESS
)

:: ========================================================
:: BUILD SUCCESS
:: ========================================================
:BUILD_SUCCESS
echo.
call :DRAW_BOX "BUILD SUCCESSFUL!"

if exist "dist" (
    for /r "dist" %%F in (*.exe) do (
        set "EXE_PATH=%%F"
        set "EXE_NAME=%%~nxF"
        set /a EXE_SIZE_MB=%%~zF / 1048576
        
        echo.
        if %IN_POWERSHELL%==1 (
            powershell -Command "Write-Host 'Your application is ready!' -ForegroundColor Green"
        ) else (
            echo Your application is ready!
        )
        echo.
        echo Location: !EXE_PATH!
        echo Name:     !EXE_NAME!
        echo Size:     !EXE_SIZE_MB! MB
        echo.
    )
)

echo.
echo ========================================
echo           BUILD SUMMARY
echo ========================================
echo.
echo * Python Environment: Ready
echo * Dependencies: Installed
echo * Project Structure: Initialized
echo * Build: Completed Successfully
echo.
echo Log files saved to:
echo   - %LOG_FILE%
echo.

echo.
echo Would you like to open the folder containing your application?
set /p "OPEN_FOLDER=Open folder now? (Y/N): "

if /i "!OPEN_FOLDER!"=="Y" (
    explorer "dist"
)

goto :CLEANUP

:: ========================================================
:: BUILD FAILURE
:: ========================================================
:BUILD_FAILED
echo.
echo ========================================
echo        BUILD FAILURE REPORT
echo ========================================
echo.
echo Status: Build Failed
echo Exit Code: %BUILD_EXIT_CODE%
echo.
echo Logs saved to:
echo   - %LOG_FILE%
echo   - %ERROR_LOG%
echo.

echo Would you like to view the error log?
set /p "VIEW_LOG=View error log? (Y/N): "

if /i "!VIEW_LOG!"=="Y" (
    if exist "%ERROR_LOG%" (
        notepad "%ERROR_LOG%"
    )
)

goto :CLEANUP

:: ========================================================
:: CLEANUP
:: ========================================================
:CLEANUP
echo.
call :COLOR_STEP "Cleanup Complete"

call deactivate 2>nul

echo.
call :DRAW_BOX "Thank you for using Build System v2.0"

if %IN_POWERSHELL%==1 (
    powershell -Command "Write-Host 'All done!' -ForegroundColor Green"
) else (
    echo All done!
)

echo.

pause
exit /b %BUILD_EXIT_CODE%