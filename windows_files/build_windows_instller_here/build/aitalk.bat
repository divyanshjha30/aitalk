@echo off
setlocal

:: Use the directory this script is in
set "SCRIPT_DIR=%~dp0"
set "AITALK_EXE=%SCRIPT_DIR%aitalk.exe"

:: Parse arguments
set ARG1=%1
set ARG2=%2
set ARG3=%3

:: --create-project
if "%ARG1%"=="--create-project" (
    shift
    "%AITALK_EXE%" --create-project %ARG2%
    exit /b
)

:: --explain-X (match like --explain-5)
echo %ARG1% | findstr /r "^--explain-[0-9][0-9]*$" >nul
if %errorlevel%==0 (
    "%AITALK_EXE%" %ARG1%
    exit /b
)

:: --chat
if "%ARG1%"=="--chat" (
    "%AITALK_EXE%" --chat
    exit /b
)

:: --git-summary
if "%ARG1%"=="--git-summary" (
    "%AITALK_EXE%" --git-summary
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
    "%AITALK_EXE%" --summarise "%ARG2%" "%ARG3%"
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
