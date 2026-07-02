@echo off
echo ========================================
echo   Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0..\ui\backend"
if errorlevel 1 (
	echo [ERROR] Could not change directory to backend
	pause
	exit /b 1
)

echo [OK] Working directory: %CD%
echo [OK] Starting backend on http://localhost:8000
echo.

python -X utf8 app.py

pause
