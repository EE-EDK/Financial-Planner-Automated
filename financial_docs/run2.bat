@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ========================================================
:: SPECIALIZED FINANCIAL HUB BUILDER for Category-Based Excel Template
:: Works with ANY number of entries - automatically detects categories from headers
:: Template format: Date | Description | Category Columns... | Balance
:: ========================================================

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=%~nx0"

:: Detect PowerShell for colored output
set "PS_AVAILABLE=0"
where powershell >nul 2>&1
if %ERRORLEVEL%==0 set "PS_AVAILABLE=1"

:: Timestamp for logs
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "dt=%%I"
if defined dt (
    set "TIMESTAMP=%dt:~0,8%_%dt:~8,6%"
) else (
    set "TIMESTAMP=%random%_%random%"
)

:: Initialize logging
set "LOG_DIR=%SCRIPT_DIR%logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" 2>nul
set "LOG_FILE=%LOG_DIR%\build2_%TIMESTAMP%.log"

:: ========================================================
:: COLOR HELPER FUNCTIONS
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
    exit /b

:COLOR_ERROR
    if %PS_AVAILABLE%==1 (
        powershell -NoProfile -Command "Write-Host '[ERROR]' -ForegroundColor Red -NoNewline; Write-Host ' %~1'" 2>nul
        if !ERRORLEVEL! NEQ 0 echo [ERROR] %~1
    ) else (
        echo [ERROR] %~1
    )
    echo [ERROR] %~1 >> "%LOG_FILE%" 2>nul
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

cls
echo.
call :DRAW_BOX "CATEGORY-BASED EXCEL FINANCIAL HUB BUILDER"

if %PS_AVAILABLE%==1 (
    powershell -NoProfile -Command "Write-Host 'Specialized builder for category-based Excel format' -ForegroundColor Green" 2>nul
    powershell -NoProfile -Command "Write-Host '  * Auto-detects categories from Excel headers' -ForegroundColor White" 2>nul
    powershell -NoProfile -Command "Write-Host '  * Handles ANY number of transaction entries' -ForegroundColor White" 2>nul
    powershell -NoProfile -Command "Write-Host '  * Creates balance tracking and category analysis' -ForegroundColor White" 2>nul
    powershell -NoProfile -Command "Write-Host '  * Generates enhanced HTML hub with visualizations' -ForegroundColor White" 2>nul
) else (
    echo Specialized builder for category-based Excel format
    echo   * Auto-detects categories from Excel headers
    echo   * Handles ANY number of transaction entries
    echo   * Creates balance tracking and category analysis
    echo   * Generates enhanced HTML hub with visualizations
)
echo.
pause

call :COLOR_STEP "Finding Python"

:: Check for Python
set "PYTHON_CMD=python"
set "PYTHON_FOUND=0"

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_FOUND=1"
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do call :COLOR_SUCCESS "Python found: %%V"
)

if %PYTHON_FOUND%==0 (
    python3 --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_FOUND=1"
        set "PYTHON_CMD=python3"
        for /f "tokens=2" %%V in ('python3 --version 2^>^&1') do call :COLOR_SUCCESS "Python found: %%V"
    )
)

if %PYTHON_FOUND%==0 (
    py --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_FOUND=1"
        set "PYTHON_CMD=py"
        for /f "tokens=2" %%V in ('py --version 2^>^&1') do call :COLOR_SUCCESS "Python found: %%V"
    )
)

if %PYTHON_FOUND%==0 (
    call :COLOR_ERROR "Python not found!"
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

call :COLOR_STEP "Checking Excel File"

:: Look for Excel files with budget or category-based format
set "EXCEL_FILE="
set "SEARCH_DIR=%SCRIPT_DIR%Archive\raw\exports"

call :COLOR_INFO "Searching for Excel files in exports directory..."

:: Find most recent Excel file
for /f "delims=" %%F in ('dir /b /o-d "%SEARCH_DIR%\*.xlsx" "%SEARCH_DIR%\*.xls" 2^>nul') do (
    if not "%%F"=="" (
        set "EXCEL_FILE=%SEARCH_DIR%\%%F"
        goto :FOUND_EXCEL
    )
)

:FOUND_EXCEL
if "%EXCEL_FILE%"=="" (
    call :COLOR_ERROR "No Excel file found!"
    echo.
    echo Searched in: %SEARCH_DIR%
    echo.
    echo Please place your Excel budget file (with any number of entries) in:
    echo   %SCRIPT_DIR%Archive\raw\exports\
    echo.
    echo Expected format:
    echo   Col 1: Date
    echo   Col 2: Description
    echo   Col 3-N: Category columns (Auto, Utilities, Medical, etc.)
    echo   Last Col: Balance
    echo.
    pause
    exit /b 1
) else (
    call :COLOR_SUCCESS "Excel file found"
    echo File: %EXCEL_FILE%
    for %%F in ("%EXCEL_FILE%") do (
        set /a FILE_SIZE_KB=%%~zF / 1024
        call :COLOR_INFO "Size: !FILE_SIZE_KB! KB"
    )
)

call :COLOR_STEP "Building Financial Hub"

set "BUILD_SCRIPT=%SCRIPT_DIR%build_all2.py"

if not exist "%BUILD_SCRIPT%" (
    call :COLOR_ERROR "build_all2.py not found!"
    echo.
    echo Expected: %BUILD_SCRIPT%
    echo.
    pause
    exit /b 1
)

echo Running specialized build script...
echo.
echo Build script: %BUILD_SCRIPT%
echo Working directory: %SCRIPT_DIR%
echo Python: %PYTHON_CMD%
echo.

pushd "%SCRIPT_DIR%"
"%PYTHON_CMD%" "%BUILD_SCRIPT%" %*
set "BUILD_EXIT_CODE=!ERRORLEVEL!"
popd

if %BUILD_EXIT_CODE% NEQ 0 (
    call :COLOR_ERROR "Build failed with exit code: %BUILD_EXIT_CODE%"
    echo.
    echo Check the output above for details.
    echo Log file: %LOG_FILE%
    echo.
    pause
    exit /b %BUILD_EXIT_CODE%
)

call :COLOR_SUCCESS "Build completed successfully!"
echo.

:: Check for output
if exist "%SCRIPT_DIR%financial_hub2.html" (
    for %%F in ("%SCRIPT_DIR%financial_hub2.html") do set "HTML_SIZE=%%~zF"
    set /a HTML_SIZE_KB=!HTML_SIZE! / 1024
    echo.
    call :COLOR_SUCCESS "Financial Hub Created!"
    echo Name: financial_hub2.html
    echo Location: %SCRIPT_DIR%financial_hub2.html
    echo Size: !HTML_SIZE_KB! KB
    echo.

    set /p "OPEN_HTML=Open Financial Hub in browser? (Y/N): "
    if /i "!OPEN_HTML!"=="Y" (
        echo.
        call :COLOR_INFO "Opening dashboard..."
        start "" "%SCRIPT_DIR%financial_hub2.html"
    )
)

echo.
set /p "OPEN_FOLDER=Open project folder? (Y/N): "
if /i "!OPEN_FOLDER!"=="Y" (
    echo Opening folder...
    start "" "%SCRIPT_DIR%"
)

echo.
call :DRAW_BOX "Thank you for using Category-Based Excel Builder"
echo Log saved to: %LOG_FILE%
echo.
echo This builder works with ANY number of transaction entries!
echo Just maintain the format: Date | Description | Categories | Balance
echo.
pause
exit /b %BUILD_EXIT_CODE%
