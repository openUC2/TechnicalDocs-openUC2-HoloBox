#!/usr/bin/env bash
# Complete setup script for HoloBox with camera server autostart and Access Point

set -e

echo "=========================================="
echo "HoloBox Complete Setup"
echo "=========================================="

# Configuration
INSTALL_DIR="/opt/holobox"
SERVICE_USER="pi"
REPO_DIR="/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root. Please run as a regular user (pi)."
   exit 1
fi

echo "Setting up HoloBox system..."
echo "Installation directory: $INSTALL_DIR"
echo "Service user: $SERVICE_USER"
echo ""

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python dependencies
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    hostapd \
    dnsmasq \
    iptables-persistent \
    git \
    curl \
    wget

# Create installation directory
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Copy software files
echo "Copying HoloBox software..."
cp -r "$REPO_DIR/Software"/* "$INSTALL_DIR/"

# Set permissions
chmod +x "$INSTALL_DIR"/*.sh

# Create virtual environment and install Python dependencies
echo "Setting up Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install fastapi uvicorn numpy opencv-python-headless pydantic

# Try to install picamera2 (might fail on non-Pi systems)
pip install picamera2 || echo "Warning: picamera2 installation failed - using mock camera"

# Update service registration script to use venv
echo "Updating service registration..."
sed -i "s|ExecStart=/usr/bin/python3|ExecStart=$INSTALL_DIR/venv/bin/python|g" "$INSTALL_DIR/registerservice.sh"
sed -i "s|WorkingDirectory=/opt/holobox/Software|WorkingDirectory=$INSTALL_DIR|g" "$INSTALL_DIR/registerservice.sh"

# Register and enable the camera service
echo "Registering camera service..."
bash "$INSTALL_DIR/registerservice.sh"

# Set up log directory
sudo mkdir -p /var/log/holobox
sudo chown "$SERVICE_USER:$SERVICE_USER" /var/log/holobox

# Configure service for logging
sudo tee /etc/systemd/system/holobox-camera.service > /dev/null <<EOF
[Unit]
Description=HoloBox Camera API Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/streamlined_camera_api.py --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/log/holobox/camera.log
StandardError=append:/var/log/holobox/camera.log

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable holobox-camera.service

# Setup Access Point (but don't enable by default)
echo "Preparing Access Point configuration..."
echo "Access Point setup script is ready at: $INSTALL_DIR/setup_access_point.sh"
echo "WiFi client setup script is ready at: $INSTALL_DIR/setup_wifi_client.sh"

# Create a simple system info script
sudo tee /usr/local/bin/holobox-info > /dev/null <<EOF
#!/bin/bash
echo "HoloBox System Information"
echo "=========================="
echo "Service Status:"
sudo systemctl status holobox-camera.service --no-pager -l
echo ""
echo "Network Status:"
ip addr show wlan0 2>/dev/null || echo "wlan0 not available"
iwgetid 2>/dev/null || echo "Not connected to WiFi"
echo ""
echo "Access logs:"
sudo tail -n 10 /var/log/holobox/camera.log 2>/dev/null || echo "No logs yet"
EOF

sudo chmod +x /usr/local/bin/holobox-info

# Create desktop shortcut (if desktop environment is available)
if [ -d "/home/$SERVICE_USER/Desktop" ]; then
    tee "/home/$SERVICE_USER/Desktop/HoloBox.desktop" > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=HoloBox Camera
Comment=Open HoloBox Camera Interface
Exec=chromium-browser http://localhost:8000/static/
Icon=applications-multimedia
Terminal=false
Categories=Multimedia;
EOF
    chmod +x "/home/$SERVICE_USER/Desktop/HoloBox.desktop"
fi

echo ""
echo "=========================================="
echo "HoloBox Setup Complete!"
echo "=========================================="
echo ""
echo "Services installed:"
echo "  - holobox-camera.service (enabled)"
echo ""
echo "Available commands:"
echo "  - holobox-info                    Show system status"
echo "  - $INSTALL_DIR/setup_access_point.sh    Setup Access Point mode"
echo "  - $INSTALL_DIR/setup_wifi_client.sh     Connect to WiFi network"
echo ""
echo "Web interface available at:"
echo "  - Local: http://localhost:8000/static/"
echo "  - Network: http://[YOUR-IP]:8000/static/"
echo ""
echo "To start the service now:"
echo "  sudo systemctl start holobox-camera.service"
echo ""
echo "To enable Access Point mode:"
echo "  bash $INSTALL_DIR/setup_access_point.sh"
echo ""
echo "Logs are available at:"
echo "  /var/log/holobox/camera.log"
echo ""
echo "The system is ready! Reboot recommended to ensure all services start properly."