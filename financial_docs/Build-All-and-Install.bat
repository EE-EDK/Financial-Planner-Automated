@echo off
setlocal

echo ========================================================
echo  Checking System Requirements
echo ========================================================

:: 1. Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not found on this system.
    echo Attempting to install Python 3.12 via Winget...
    
    :: Uses Windows Package Manager to install Python
    winget install -e --id Python.Python.3.12
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Automatic installation failed. 
        echo Please install Python manually from python.org and try again.
        pause
        exit /b
    )
    
    echo Python installed. Please close and reopen this script to refresh system paths.
    pause
    exit /b
) ELSE (
    echo Python is present.
)

:: 2. Create a local Virtual Environment (Fixes permission/path errors)
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: 3. Activate the Virtual Environment
call venv\Scripts\activate

:: 4. Ensure PyInstaller is installed inside this environment
echo Checking for PyInstaller...
pip show pyinstaller >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    :: If you have a requirements.txt, uncomment the next line:
    :: pip install -r requirements.txt
)

echo ========================================================
echo  Running build_all.py
echo ========================================================

:: 5. Run your build script
python build_all.py

echo.
echo Done.
pause