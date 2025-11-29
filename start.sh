#!/bin/bash

# ============================================
# 🚕 TAXI SYSTEM - START SCRIPT (Linux/Mac)
# ============================================

echo ""
echo "🚕 TAXI SYSTEM STARTING..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8+"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/update requirements
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Show menu
echo ""
echo "============================================"
echo "🚕 TAXI SYSTEM MENU"
echo "============================================"
echo ""
echo "1. Start Telegram Bot (🤖)"
echo "2. Initialize Database (💾)"
echo "3. View Database (📊)"
echo "4. Exit"
echo ""
read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🤖 Starting Telegram Bot..."
        echo "📱 Bot Commands:"
        echo "   /start - Start"
        echo "   /help - Help"
        echo "   /profile - Profile"
        echo ""
        python3 taxi.py
        ;;
    2)
        echo ""
        echo "💾 Initializing database..."
        python3 -c "from taxi import init_system; init_system(); print('✅ Database initialized!')"
        ;;
    3)
        echo ""
        echo "📊 Database info:"
        python3 -c "from taxi import SessionLocal, User; db = SessionLocal(); print(f'Total Users: {db.query(User).count()}'); db.close()"
        ;;
    4)
        echo "Goodbye!"
        ;;
    *)
        echo "Invalid option!"
        ;;
esac
