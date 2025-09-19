#!/bin/bash

# HoloBox Camera Service Setup Script
# This script configures the system to run the camera API on port 80

set -e

echo "Setting up HoloBox Camera Service..."

# Check if running as root for service installation
if [[ $EUID -ne 0 ]]; then
   echo "Please run this script as root (use sudo)" 
   exit 1
fi

# Get the actual user who called sudo
ACTUAL_USER=${SUDO_USER:-$USER}
SOFTWARE_DIR="/home/$ACTUAL_USER/Software"

echo "Installing for user: $ACTUAL_USER"
echo "Software directory: $SOFTWARE_DIR"

# Ensure software directory exists
if [ ! -d "$SOFTWARE_DIR" ]; then
    echo "Error: Software directory not found at $SOFTWARE_DIR"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
apt-get update
apt-get install -y python3-pip python3-dev

# Allow Python to bind to port 80 without root
echo "Configuring Python to bind to port 80..."
setcap 'cap_net_bind_service=+ep' /usr/bin/python3

# Install systemd service
echo "Installing systemd service..."
sed "s|/home/pi/Software|$SOFTWARE_DIR|g" "$SOFTWARE_DIR/holobox-camera.service" > /etc/systemd/system/holobox-camera.service
sed -i "s|User=pi|User=$ACTUAL_USER|g" /etc/systemd/system/holobox-camera.service
sed -i "s|Group=pi|Group=$ACTUAL_USER|g" /etc/systemd/system/holobox-camera.service

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable holobox-camera.service

# Configure firewall if ufw is active
if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
    echo "Configuring firewall..."
    ufw allow 80/tcp
    ufw allow 22/tcp  # Keep SSH open
fi

echo "Setup complete!"
echo ""
echo "To start the service now:"
echo "  sudo systemctl start holobox-camera"
echo ""
echo "To check service status:"
echo "  sudo systemctl status holobox-camera"
echo ""
echo "To view logs:"
echo "  journalctl -u holobox-camera -f"
echo ""
echo "The service will start automatically on boot."
echo "Access the web interface at: http://192.168.4.1/"