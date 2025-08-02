#!/bin/bash

echo "🚀 Starting MT5 Flask Application with Virtual Display"

# Set up virtual display
echo "📺 Setting up virtual display..."
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait a moment for Xvfb to start
sleep 2

# Test Wine with virtual display
echo "🍷 Testing Wine with virtual display..."
DISPLAY=:99 wine python -c "import MetaTrader5; print('MT5 available')" 2>/dev/null && {
    echo "✅ MT5 is available in Wine"
} || {
    echo "⚠️  MT5 not available in Wine, but continuing..."
}

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
fi

# Run the Flask application
echo "🌐 Starting Flask application..."
python3 main.py 