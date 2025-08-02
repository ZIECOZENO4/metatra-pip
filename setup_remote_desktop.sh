#!/bin/bash

echo "🖥️  Setting up Remote Desktop Access"

# Update system
sudo apt update

# Install desktop environment
echo "📦 Installing desktop environment..."
sudo apt install -y xfce4 xfce4-goodies

# Install VNC server
echo "🔧 Installing VNC server..."
sudo apt install -y tightvncserver

# Install xrdp (RDP server)
echo "🌐 Installing RDP server..."
sudo apt install -y xrdp

# Configure xrdp
echo "⚙️  Configuring RDP..."
sudo systemctl enable xrdp
sudo systemctl start xrdp

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 3389  # RDP
sudo ufw allow 5901  # VNC

# Create VNC startup script
echo "📝 Creating VNC startup script..."
mkdir -p ~/.vnc
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF

chmod +x ~/.vnc/xstartup

echo "✅ Remote desktop setup complete!"
echo ""
echo "🌐 RDP Connection:"
echo "   - Use Windows Remote Desktop Connection"
echo "   - Connect to: $(hostname -I | awk '{print $1}')"
echo "   - Port: 3389"
echo ""
echo "🔧 VNC Connection:"
echo "   - Use VNC Viewer"
echo "   - Connect to: $(hostname -I | awk '{print $1}'):5901"
echo "   - Set password with: vncserver"
echo ""
echo "📱 Web Terminal:"
echo "   - Install ttyd: sudo apt install ttyd"
echo "   - Run: ttyd -p 7681 bash"
echo "   - Access: http://$(hostname -I | awk '{print $1}'):7681" 