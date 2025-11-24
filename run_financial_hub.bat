@echo off
REM Financial Hub Builder - Windows Batch Launcher
REM This ensures the script runs from the correct directory

cd /d "%~dp0"
echo ================================================================================
echo Financial Hub Builder
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if financial_docs exists
if not exist "financial_docs\build_all.py" (
    echo ERROR: financial_docs\build_all.py not found
    echo Please run this script from the repository root directory
    pause
    exit /b 1
)

echo Running Financial Hub Builder...
echo.

REM Run the builder
python financial_docs\build_all.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo Build completed successfully!
    echo ================================================================================
    echo.
    echo To view your financial hub:
    echo   - Open: financial_docs\financial_hub.html
    echo.
) else (
    echo.
    echo ================================================================================
    echo Build failed with errors
    echo ================================================================================
    echo.
)

pause
