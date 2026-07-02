@echo off
REM AI Software Company UI - Start Script for Windows

echo ========================================
echo   AI Software Company UI
echo ========================================
echo.

REM Check if Ollama is running
echo 1. Checking Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not running!
    echo Please start Ollama first: ollama serve
    pause
    exit /b 1
)
echo [OK] Ollama is running
echo.

REM Start Backend
echo 2. Starting Backend...
cd backend
start "AI Software Company Backend" cmd /k "python -X utf8 app.py"
echo [OK] Backend started
echo     Running on: http://localhost:8000
echo.

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
echo 3. Starting Frontend...
cd ..\frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
)

start "AI Software Company Frontend" cmd /k "npm run dev"
echo [OK] Frontend started
echo     Running on: http://localhost:3000
echo.

echo ========================================
echo   AI Software Company UI is ready!
echo ========================================
echo.
echo Open your browser: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
