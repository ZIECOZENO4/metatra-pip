#!/usr/bin/env python3
"""
Script to create requirements.txt for MetaTrader5 Flask application
"""

import subprocess
import sys

def create_requirements():
    """Create requirements.txt with all necessary dependencies"""
    
    # Define the required packages with versions
    requirements = [
        "Flask==3.0.3",
        "flask-cors==6.0.1",
        "blinker==1.9.0",
        "click==8.2.1",
        "colorama==0.4.6",
        "itsdangerous==2.2.0",
        "Jinja2==3.1.6",
        "MarkupSafe==3.0.2",
        "Werkzeug==3.1.3",
        "numpy==2.3.1",
        "pandas==2.3.1",
        "python-dateutil==2.9.0.post0",
        "pytz==2025.2",
        "six==1.17.0",
        "tzdata==2025.2"
    ]
    
    # Write requirements to file
    with open('requirements.txt', 'w') as f:
        for req in requirements:
            f.write(req + '\n')
    
    print("✅ requirements.txt created successfully!")
    print(f"📦 Added {len(requirements)} packages")
    
    # Show the contents
    print("\n📋 Contents of requirements.txt:")
    with open('requirements.txt', 'r') as f:
        print(f.read())

def install_requirements():
    """Install the requirements"""
    try:
        print("\n🔧 Installing requirements...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully!")
        else:
            print("❌ Error installing requirements:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 Creating requirements.txt for MetaTrader5 Flask Application")
    print("=" * 60)
    
    # Create requirements file
    create_requirements()
    
    # Ask if user wants to install
    response = input("\n🤔 Do you want to install the requirements now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        install_requirements()
    else:
        print("\n💡 To install later, run: pip install -r requirements.txt")
    
    print("\n✨ Setup complete!")

if __name__ == "__main__":
    main() 