#!/bin/bash

# VPNGUARD Installer Script for Linux
# This script automates the installation of system dependencies, 
# python environments, systemd background services, and desktop shortcuts.

set -e # Exit immediately if a command exits with a non-zero status

# 1. Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "❌ Error: Please run this installer with root privileges (sudo ./install.sh)"
  exit 1
fi

echo "🚀 Starting VPNGUARD Installation..."
PROJECT_DIR=$(pwd)
USERNAME=${SUDO_USER:-$USER}

# 2. Detect OS and install dependencies
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    
    echo "📦 Detected OS: $OS"
    if [[ "$OS" == "arch" || "$OS" == "manjaro" ]]; then
        echo "🔧 Installing system dependencies via pacman..."
        pacman -Syu --noconfirm
        pacman -S --noconfirm git python npm libpcap pango cairo gdk-pixbuf2 python-pip
    elif [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        echo "🔧 Installing system dependencies via apt..."
        apt-get update
        apt-get install -y git python3 python3-venv python3-pip npm libpcap-dev libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0
    elif [[ "$OS" == "fedora" || "$OS" == "rhel" || "$OS" == "centos" ]]; then
        echo "🔧 Installing system dependencies via dnf..."
        dnf update -y
        dnf install -y git python3 python3-pip npm libpcap-devel pango cairo gdk-pixbuf2
    else
        echo "⚠️ Unsupported OS for automatic dependency installation. Please install libpcap, Node.js, and Python manually."
    fi
else
    echo "⚠️ Cannot detect OS. Please ensure libpcap, Node.js, and Python are installed."
fi

# 3. Setup Backend (Python Daemon)
echo "🐍 Setting up Python Virtual Environment..."
if [ ! -d "pandas_env" ]; then
    python3 -m venv pandas_env
fi

# Fix ownership so npm and pip don't complain later about root ownership of files
chown -R $USERNAME:$USERNAME $PROJECT_DIR

# Run pip as the standard user to avoid root pip warnings
echo "📦 Installing Python packages..."
sudo -u $USERNAME ./pandas_env/bin/pip install weasyprint jinja2 psutil scapy fastapi uvicorn

# 4. Setup Systemd Service
echo "⚙️ Configuring background systemd service..."
SERVICE_PATH="/etc/systemd/system/vpnguard-analyzer.service"

cat <<EOF > $SERVICE_PATH
[Unit]
Description=VPNGUARD Packet Capture & Analysis Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/pandas_env/bin/python -m backend.api.main
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vpnguard-analyzer
systemctl restart vpnguard-analyzer
echo "✅ Backend daemon started successfully!"

# 5. Build Frontend (React + Electron)
echo "⚛️ Building the React Dashboard..."
cd $PROJECT_DIR/dashboard

# Run npm install as the standard user
sudo -u $USERNAME npm install

# 6. Create Desktop Shortcut
echo "🖥️ Creating Desktop Application Shortcut..."
DESKTOP_ENTRY_PATH="/usr/share/applications/vpnguard.desktop"

cat <<EOF > $DESKTOP_ENTRY_PATH
[Desktop Entry]
Name=VPNGUARD
Comment=IPsec VPN Security Analyzer
Exec=sh -c 'cd $PROJECT_DIR/dashboard && npm start'
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=System;Security;Network;
EOF

chmod +x $DESKTOP_ENTRY_PATH
echo "✅ VPNGUARD Desktop Shortcut added to your application launcher!"

echo ""
echo "🎉 INSTALLATION COMPLETE! 🎉"
echo "You can now launch 'VPNGUARD' from your Linux application menu,"
echo "or navigate to the dashboard directory and run 'npm start'."
echo "The background analysis engine is already running securely as a service."
