@echo off
echo ========================================
echo   Starting Backend Server (CrewAI Mode)
echo ========================================
echo.

cd /d "%~dp0..\ui\backend"
if errorlevel 1 (
	echo [ERROR] Could not change directory to backend: %~dp0..\ui\backend
	pause
	exit /b 1
)

:: Use the Python executable from the .venv-crewai environment
..\..\.venv-crewai\Scripts\python.exe app.py

pause
