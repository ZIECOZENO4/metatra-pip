#!/bin/bash

echo "🚀 MetaTrader5 Installation Script for VPS"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Running as root - this is fine for VPS"
else
   echo "❌ This script needs to be run as root or with sudo"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update

# Install Wine
echo "🍷 Installing Wine..."
if ! command_exists wine; then
    apt install -y wine wine64 wine32 winbind
else
    echo "✅ Wine already installed"
fi

# Check Wine installation
echo "🔍 Checking Wine installation..."
wine --version

# Download Python for Windows
echo "🐍 Downloading Python for Windows..."
PYTHON_VERSION="3.9.13"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe"
PYTHON_INSTALLER="python-${PYTHON_VERSION}-amd64.exe"

if [ ! -f "$PYTHON_INSTALLER" ]; then
    wget "$PYTHON_URL"
else
    echo "✅ Python installer already downloaded"
fi

# Install Python in Wine
echo "🔧 Installing Python in Wine..."
if ! wine python --version >/dev/null 2>&1; then
    wine "$PYTHON_INSTALLER" /quiet InstallAllUsers=1 PrependPath=1
    echo "⏳ Waiting for installation to complete..."
    sleep 10
else
    echo "✅ Python already installed in Wine"
fi

# Test Python in Wine
echo "🧪 Testing Python in Wine..."
wine python --version

# Install MT5
echo "📈 Installing MetaTrader5..."
wine python -m pip install MetaTrader5==5.0.5120

# Test MT5 installation
echo "🧪 Testing MT5 installation..."
wine python -c "import MetaTrader5; print('✅ MT5 installed successfully')" 2>/dev/null || {
    echo "❌ MT5 installation failed"
    echo "🔧 Trying alternative installation method..."
    wine python -m pip install --upgrade pip
    wine python -m pip install MetaTrader5==5.0.5120 --force-reinstall
}

# Create test script
echo "📝 Creating MT5 test script..."
cat > test_mt5.py << 'EOF'
import MetaTrader5 as mt5

print("Testing MT5 installation...")
if mt5.initialize():
    print("✅ MT5 initialized successfully")
    mt5.shutdown()
else:
    print("⚠️  MT5 initialized but no terminal found (this is normal on VPS)")
EOF

# Test with Wine
echo "🧪 Running MT5 test with Wine..."
wine python test_mt5.py

echo "✨ Installation complete!"
echo "💡 To run your Flask app: python main_wine.py" 