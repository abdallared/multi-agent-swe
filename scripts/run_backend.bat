@echo off
echo ========================================
echo   Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0..\ui\backend"
if errorlevel 1 (
	echo [ERROR] Could not change directory to backend: %~dp0..\ui\backend
	pause
	exit /b 1
)

python app.py

pause
