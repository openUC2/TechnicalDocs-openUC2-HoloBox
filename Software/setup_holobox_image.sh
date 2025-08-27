#!/usr/bin/env bash
# HoloBox setup script optimized for SD card image building
# This version is designed to work in a chroot environment during image creation

set -e

echo "=========================================="
echo "HoloBox SD Card Image Setup"
echo "=========================================="

# Configuration for image building
INSTALL_DIR="/opt/holobox"
SERVICE_USER="pi"
REPO_DIR="/opt/holobox-install"

echo "Setting up HoloBox system for SD card image..."
echo "Installation directory: $INSTALL_DIR"
echo "Service user: $SERVICE_USER"
echo ""

# Ensure we're in the right environment
if [ ! -d "$REPO_DIR" ]; then
    echo "Error: Source directory $REPO_DIR not found"
    echo "This script is designed for SD card image building"
    exit 1
fi

# Create pi user if it doesn't exist (for image building)
if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
    echo "Creating user: $SERVICE_USER"
    useradd -m -s /bin/bash "$SERVICE_USER"
    usermod -aG sudo "$SERVICE_USER"
    echo "$SERVICE_USER:holobox123" | chpasswd
fi

# Update system packages (should be done in image build)
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required system packages
echo "Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    hostapd \
    dnsmasq \
    iptables-persistent \
    git \
    curl \
    wget \
    openssh-server

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Copy software files
echo "Copying HoloBox software..."
cp -r "$REPO_DIR"/* "$INSTALL_DIR/"
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Set permissions
chmod +x "$INSTALL_DIR"/*.sh

# Create virtual environment and install Python dependencies
echo "Setting up Python virtual environment..."
cd "$INSTALL_DIR"
sudo -u "$SERVICE_USER" python3 -m venv venv
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip

# Install Python packages from requirements
echo "Installing Python packages..."
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
else
    # Fallback to manual installation
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install \
        fastapi==0.110.0 \
        uvicorn[standard]==0.29.0 \
        numpy==1.26.4 \
        opencv-python-headless==4.10.0.82 \
        pydantic==2.7.1
    
    # Try to install picamera2 (might fail on ARM64 in emulation)
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install picamera2==0.3.11 || echo "Warning: picamera2 installation failed - will use mock camera"
fi

# Set up log directory
echo "Setting up logging..."
mkdir -p /var/log/holobox
chown "$SERVICE_USER:$SERVICE_USER" /var/log/holobox

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/holobox-camera.service << EOF
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
systemctl daemon-reload
systemctl enable holobox-camera.service

# Create system info script
echo "Creating system utilities..."
cat > /usr/local/bin/holobox-info << 'EOF'
#!/bin/bash
echo "HoloBox System Information"
echo "=========================="
echo "Service Status:"
systemctl status holobox-camera.service --no-pager -l
echo ""
echo "Network Status:"
ip addr show wlan0 2>/dev/null || echo "wlan0 not available"
iwgetid 2>/dev/null || echo "Not connected to WiFi"
echo ""
echo "Access logs:"
tail -n 10 /var/log/holobox/camera.log 2>/dev/null || echo "No logs yet"
EOF

chmod +x /usr/local/bin/holobox-info

# Create desktop shortcut (if desktop environment is available)
if [ -d "/home/$SERVICE_USER/Desktop" ]; then
    echo "Creating desktop shortcut..."
    cat > "/home/$SERVICE_USER/Desktop/HoloBox.desktop" << EOF
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
    chown "$SERVICE_USER:$SERVICE_USER" "/home/$SERVICE_USER/Desktop/HoloBox.desktop"
fi

# Enable SSH service
echo "Enabling SSH service..."
systemctl enable ssh

# Configure SSH for security
if [ -f /etc/ssh/sshd_config ]; then
    # Backup original config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Enable SSH but with reasonable security
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
    
    # Add SSH banner
    cat > /etc/ssh/banner << 'BANNER_EOF'
╔══════════════════════════════════════════╗
║             HoloBox System               ║
║          SSH Access Enabled             ║
╚══════════════════════════════════════════╝

BANNER_EOF
    echo "Banner /etc/ssh/banner" >> /etc/ssh/sshd_config
fi

# Create welcome message
echo "Creating welcome message..."
cat > /etc/motd << 'EOF'

╔══════════════════════════════════════════╗
║             HoloBox System               ║
╚══════════════════════════════════════════╝

Welcome to the HoloBox SD Card Image!

🌐 Web Interface: http://localhost:8000/static/
📱 Access Point: Connect to openUC2-XXXXX-YYYYY (password: holobox123)
🔗 Gateway IP: http://192.168.4.1:8000/static/

💡 Commands:
   holobox-info                           - Show system status
   sudo /opt/holobox/setup_access_point.sh - Enable Access Point mode
   sudo /opt/holobox/setup_wifi_client.sh  - Connect to WiFi

📖 Documentation: https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox

EOF

# Create a first-boot setup script
echo "Creating first-boot configuration..."
cat > /opt/holobox/first-boot.sh << 'EOF'
#!/bin/bash
# First boot configuration script

# Expand filesystem on first boot
if [ ! -f /opt/holobox/.expanded ]; then
    echo "Expanding filesystem on first boot..."
    raspi-config --expand-rootfs
    touch /opt/holobox/.expanded
    
    # Schedule reboot after expansion
    echo "Filesystem expanded. Rebooting in 10 seconds..."
    sleep 10
    reboot
fi

# Generate unique hostname based on MAC address
MAC=$(cat /sys/class/net/wlan0/address 2>/dev/null | tr -d ':' | tail -c 6)
if [ ! -z "$MAC" ] && [ ! -f /opt/holobox/.hostname-set ]; then
    NEW_HOSTNAME="holobox-$MAC"
    echo "Setting hostname to: $NEW_HOSTNAME"
    hostnamectl set-hostname "$NEW_HOSTNAME"
    
    # Update /etc/hosts
    sed -i "s/127.0.1.1.*/127.0.1.1\t$NEW_HOSTNAME/" /etc/hosts
    
    touch /opt/holobox/.hostname-set
fi

# Start HoloBox service if not running
if ! systemctl is-active --quiet holobox-camera.service; then
    systemctl start holobox-camera.service
fi
EOF

chmod +x /opt/holobox/first-boot.sh

# Create systemd service for first-boot script
cat > /etc/systemd/system/holobox-first-boot.service << 'EOF'
[Unit]
Description=HoloBox First Boot Configuration
After=network.target
Before=holobox-camera.service

[Service]
Type=oneshot
ExecStart=/opt/holobox/first-boot.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl enable holobox-first-boot.service

echo ""
echo "=========================================="
echo "HoloBox SD Card Image Setup Complete!"
echo "=========================================="
echo ""
echo "Services installed and enabled:"
echo "  - holobox-camera.service"
echo "  - holobox-first-boot.service"
echo "  - ssh.service"
echo ""
echo "Available commands:"
echo "  - holobox-info                    Show system status"
echo "  - /opt/holobox/setup_access_point.sh    Setup Access Point mode"
echo "  - /opt/holobox/setup_wifi_client.sh     Connect to WiFi network"
echo ""
echo "Web interface available at:"
echo "  - Local: http://localhost:8000/static/"
echo "  - Network: http://[device-ip]:8000/static/"
echo "  - Access Point: http://192.168.4.1:8000/static/"
echo ""
echo "Default credentials:"
echo "  - SSH User: pi"
echo "  - SSH Password: holobox123"
echo "  - WiFi Hotspot Password: holobox123"
echo ""
echo "Image is ready for deployment!"