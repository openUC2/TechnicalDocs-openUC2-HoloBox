#!/usr/bin/env bash
# Setup Raspberry Pi as WiFi Access Point for HoloBox

set -e

# Default configuration
SSID="HoloBox-$(hostname | tail -c 5)"
PASSPHRASE="holobox123"
INTERFACE="wlan0"
IP_RANGE="192.168.4.0/24"
GATEWAY="192.168.4.1"

echo "Setting up HoloBox Access Point..."
echo "SSID: $SSID"
echo "Interface: $INTERFACE"
echo "IP Range: $IP_RANGE"

# Update package list
sudo apt-get update

# Install required packages
echo "Installing hostapd and dnsmasq..."
sudo apt-get install -y hostapd dnsmasq

# Stop services to configure them
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

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

# Enable services
echo "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo systemctl enable restore-iptables

echo "Access Point setup complete!"
echo "SSID: $SSID"
echo "Password: $PASSPHRASE"
echo "Gateway IP: $GATEWAY"
echo ""
echo "Please reboot the system to activate the Access Point:"
echo "sudo reboot"
echo ""
echo "After reboot, devices can connect to the $SSID network"
echo "and access the camera interface at http://$GATEWAY:8000/static/"