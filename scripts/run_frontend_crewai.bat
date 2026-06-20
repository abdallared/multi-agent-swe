@echo off
echo ========================================
echo   Starting Frontend Server (CrewAI Mode)
echo ========================================
echo.

cd /d "%~dp0..\ui\frontend"
if errorlevel 1 (
	echo [ERROR] Could not change directory to frontend: %~dp0..\ui\frontend
	pause
	exit /b 1
)

npm run dev

pause
