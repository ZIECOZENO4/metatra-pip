#!/bin/bash

echo "Setting up MetaTrader5 Flask application..."

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Installing..."
    sudo apt update
    sudo apt install python3 python3-pip python3-venv -y
fi

# Check if Wine is installed
if ! command -v wine &> /dev/null; then
    echo "Wine is not installed. Installing..."
    sudo apt update
    sudo apt install wine -y
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Check if Wine Python is available
echo "Checking Wine Python installation..."
if ! wine python --version &> /dev/null; then
    echo "Wine Python not found. You need to install Python for Windows in Wine."
    echo "Download Python installer for Windows and run: wine python-3.x.x-amd64.exe"
    echo "Then install MetaTrader5: wine python -m pip install MetaTrader5==5.0.5120"
else
    echo "Wine Python found. Installing MetaTrader5..."
    wine python -m pip install MetaTrader5==5.0.5120
fi

echo "Setup complete!"
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: python main_wine.py" 