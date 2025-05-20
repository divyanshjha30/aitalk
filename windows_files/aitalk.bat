@echo off
setlocal

:: Set paths
set "AITALK_PATH=%USERPROFILE%\Desktop\windowsaitlk\windows\aitalk.py"
set "VENV_PYTHON=%USERPROFILE%\Desktop\windowsaitlk\windows\.venv\Scripts\python.exe"

:: Check for virtual environment
if not exist "%VENV_PYTHON%" (
    echo ❌ Python virtual environment not found or not set up at %VENV_PYTHON%
    echo Please run: python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
    exit /b 1
)

:: Parse arguments
set ARG1=%1
set ARG2=%2
set ARG3=%3

:: --create-project
if "%ARG1%"=="--create-project" (
    shift
    "%VENV_PYTHON%" "%AITALK_PATH%" --create-project %ARG2%
    exit /b
)

:: --explain-X (match like --explain-5)
echo %ARG1% | findstr /r "^--explain-[0-9][0-9]*$" >nul
if %errorlevel%==0 (
    "%VENV_PYTHON%" "%AITALK_PATH%" %ARG1%
    exit /b
)

:: --chat
if "%ARG1%"=="--chat" (
    "%VENV_PYTHON%" "%AITALK_PATH%" --chat
    exit /b
)

:: --git-summary
if "%ARG1%"=="--git-summary" (
    "%VENV_PYTHON%" "%AITALK_PATH%" --git-summary
    exit /b
)

:: --summarise "<prompt>" file.txt
if "%ARG1%"=="--summarise" (
    if "%ARG2%"=="" (
        echo ❌ Missing prompt.
        exit /b 1
    )
    if not exist "%ARG3%" (
        echo ❌ File not found: %ARG3%
        exit /b 1
    )
    "%VENV_PYTHON%" "%AITALK_PATH%" --summarise "%ARG2%" "%ARG3%"
    exit /b
)

:: --help
if "%ARG1%"=="--help" (
    echo Usage:
    echo   aitalk --create-project "make a react app"
    echo   aitalk --explain-5
    echo   aitalk --git-summary
    echo   aitalk --summarise "summarise this file" file.txt
    exit /b
)

:: Fallback
echo ❌ Invalid usage.
echo Run: aitalk --help
exit /b 1
