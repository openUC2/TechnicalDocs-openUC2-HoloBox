#!/usr/bin/env bash
# Setup Raspberry Pi as WiFi Access Point for HoloBox
# Enhanced version with NetworkManager support and better diagnostics

set -e

# Default configuration  
INTERFACE="wlan0"
IP_RANGE="192.168.4.0/24"
GATEWAY="192.168.4.1"
PASSPHRASE="holobox123"

# Generate MAC-based SSID using the generate_ssid.py script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
if [ -f "$SCRIPT_DIR/generate_ssid.py" ]; then
    SSID=$(python3 "$SCRIPT_DIR/generate_ssid.py" "$INTERFACE" | tail -n 1 | cut -d' ' -f3)
else
    # Fallback if script is not available
    SSID="openUC2-$(hostname | tail -c 5)"
fi

echo "Setting up HoloBox Access Point..."
echo "SSID: $SSID"
echo "Interface: $INTERFACE"
echo "IP Range: $IP_RANGE"

# Check if NetworkManager is active and configure it properly
if systemctl is-active --quiet NetworkManager 2>/dev/null; then
    echo "Configuring NetworkManager for hotspot mode..."
    # Stop any existing connections on wlan0
    nmcli device disconnect "$INTERFACE" 2>/dev/null || true
    # Set interface to unmanaged temporarily during setup
    sudo tee /etc/NetworkManager/conf.d/99-unmanaged-devices.conf >/dev/null <<EOF
[keyfile]
unmanaged-devices=interface-name:$INTERFACE
EOF
    sudo systemctl reload NetworkManager
    sleep 2
fi

# Stop conflicting services
sudo systemctl stop hostapd dnsmasq wpa_supplicant 2>/dev/null || true

# Update package list
sudo apt-get update

# Install required packages
echo "Installing hostapd and dnsmasq..."
sudo apt-get install -y hostapd dnsmasq

# Configure static IP for wlan0
echo "Configuring static IP for $INTERFACE..."
sudo tee /etc/dhcpcd.conf.holobox > /dev/null <<EOF
# Static IP configuration for HoloBox Access Point
interface $INTERFACE
    static ip_address=$GATEWAY/24
    nohook wpa_supplicant
EOF

# Backup original dhcpcd.conf and replace
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup 2>/dev/null || true
sudo cp /etc/dhcpcd.conf.holobox /etc/dhcpcd.conf

# Configure dnsmasq
echo "Configuring dnsmasq..."
sudo tee /etc/dnsmasq.conf.holobox > /dev/null <<EOF
# HoloBox Access Point DNS/DHCP configuration
interface=$INTERFACE
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=holobox.local
local=/holobox.local/
# Prevent dnsmasq from using /etc/resolv.conf
no-resolv
# Use Google DNS for upstream
server=8.8.8.8
server=8.8.4.4
EOF

# Backup original dnsmasq.conf and replace
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true
sudo cp /etc/dnsmasq.conf.holobox /etc/dnsmasq.conf

# Configure hostapd
echo "Configuring hostapd..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<EOF
# HoloBox Access Point configuration
interface=$INTERFACE
driver=nl80211
ssid=$SSID
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSPHRASE
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Configure hostapd daemon
echo "Configuring hostapd daemon..."
sudo tee /etc/default/hostapd > /dev/null <<EOF
# Defaults for hostapd initscript
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Enable IP forwarding
echo "Enabling IP forwarding..."
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf

# Configure iptables for NAT (if eth0 is available)
echo "Configuring iptables..."
sudo iptables -t nat -F POSTROUTING 2>/dev/null || true
sudo iptables -F FORWARD 2>/dev/null || true
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o $INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i $INTERFACE -o eth0 -j ACCEPT

# Save iptables rules
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Create script to restore iptables on boot
sudo tee /etc/systemd/system/restore-iptables.service > /dev/null <<EOF
[Unit]
Description=Restore iptables rules
After=network.target

[Service]
Type=oneshot
ExecStart=/sbin/iptables-restore /etc/iptables.ipv4.nat
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Create a service to ensure proper startup order and diagnostics
sudo tee /etc/systemd/system/holobox-hotspot.service > /dev/null <<EOF
[Unit]
Description=HoloBox WiFi Hotspot Setup
After=network.target dhcpcd.service
Before=hostapd.service dnsmasq.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/bin/sleep 5
ExecStart=/bin/bash -c 'ip addr add $GATEWAY/24 dev $INTERFACE || true'
ExecStart=/bin/bash -c 'ip link set $INTERFACE up'
ExecStartPost=/bin/bash -c 'echo "Hotspot setup complete, IP: \$(ip addr show $INTERFACE | grep "inet " | awk "{print \$2}")"'

[Install]
WantedBy=multi-user.target
EOF

# Enable services
echo "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable holobox-hotspot.service
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo systemctl enable restore-iptables

echo ""
echo "=========================================="
echo "Access Point setup complete!"
echo "=========================================="
echo "SSID: $SSID"
echo "Password: $PASSPHRASE"
echo "Gateway IP: $GATEWAY"
echo ""
echo "Services enabled:"
echo "  - holobox-hotspot.service (IP configuration)"
echo "  - hostapd.service (WiFi AP)"
echo "  - dnsmasq.service (DHCP/DNS)"
echo "  - restore-iptables.service (NAT routing)"
echo ""
echo "Please reboot the system to activate the Access Point:"
echo "sudo reboot"
echo ""
echo "After reboot, devices can connect to the $SSID network"
echo "and access the camera interface at http://$GATEWAY:8000/static/"
echo ""
echo "To check status after reboot:"
echo "  sudo systemctl status holobox-hotspot hostapd dnsmasq"
echo "  ip addr show $INTERFACE"
echo "  iwconfig $INTERFACE"