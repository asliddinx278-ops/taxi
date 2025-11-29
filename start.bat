@echo off
REM ============================================
REM 🚕 TAXI SYSTEM - START SCRIPT (Windows)
REM ============================================

echo.
echo 🚕 TAXI SYSTEM STARTING...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if venv exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install/update requirements
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Show menu
echo.
echo ============================================
echo 🚕 TAXI SYSTEM MENU
echo ============================================
echo.
echo 1. Start Telegram Bot (🤖)
echo 2. Initialize Database (💾)
echo 3. View Database (📊)
echo 4. Exit
echo.
set /p choice=Choose option (1-4): 

if "%choice%"=="1" (
    echo.
    echo 🤖 Starting Telegram Bot...
    echo 📱 Bot Commands:
    echo   /start - Start
    echo   /help - Help
    echo   /profile - Profile
    echo.
    python taxi.py
) else if "%choice%"=="2" (
    echo.
    echo 💾 Initializing database...
    python -c "from taxi import init_system; init_system(); print('✅ Database initialized!')"
) else if "%choice%"=="3" (
    echo.
    echo 📊 Database info:
    python -c "from taxi import SessionLocal, User; db = SessionLocal(); print(f'Total Users: {db.query(User).count()}'); db.close()"
) else (
    echo Goodbye!
)

pause
