#!/bin/bash

# VPNGUARD - Analyzer Daemon Installer
# This script installs the Python backend as a background systemd service.

set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (e.g., sudo ./install.sh)"
  exit 1
fi

INSTALL_DIR="/opt/vpnguard-analyzer"
BACKEND_SRC="./backend"
SERVICE_FILE="/etc/systemd/system/vpnguard-analyzer.service"

echo "[*] Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

echo "[*] Copying backend source files..."
cp -r "$BACKEND_SRC/api" "$BACKEND_SRC/ml" "$BACKEND_SRC/security" "$BACKEND_SRC/requirements.txt" "$INSTALL_DIR/" 2>/dev/null || true
# Ensure main script is copied
cp "$BACKEND_SRC/api/main.py" "$INSTALL_DIR/main.py" 2>/dev/null || true

echo "[*] Setting up Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "[*] Creating systemd service file..."
cat << EOF > "$SERVICE_FILE"
[Unit]
Description=VPNGUARD Analyzer Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/api/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "[*] Reloading systemd and enabling service..."
systemctl daemon-reload
systemctl enable vpnguard-analyzer.service
systemctl restart vpnguard-analyzer.service

echo "[+] Installation complete! The VPNGUARD daemon is now running in the background."
echo "[+] You can now launch the AppImage to connect to the daemon."
