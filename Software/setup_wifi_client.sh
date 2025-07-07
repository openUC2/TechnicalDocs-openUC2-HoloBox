#!/usr/bin/env bash
# Configure Raspberry Pi to connect to external WiFi network

set -e

SSID=""
PASSPHRASE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ssid)
            SSID="$2"
            shift 2
            ;;
        --password)
            PASSPHRASE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --ssid NETWORK_NAME --password PASSWORD"
            echo "Configure Raspberry Pi to connect to external WiFi network"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if [[ -z "$SSID" ]]; then
    echo "Error: SSID is required"
    echo "Usage: $0 --ssid NETWORK_NAME --password PASSWORD"
    exit 1
fi

if [[ -z "$PASSPHRASE" ]]; then
    echo "Error: Password is required"
    echo "Usage: $0 --ssid NETWORK_NAME --password PASSWORD"
    exit 1
fi

echo "Configuring WiFi client mode..."
echo "SSID: $SSID"

# Stop access point services
echo "Stopping access point services..."
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Disable access point services
sudo systemctl disable hostapd 2>/dev/null || true
sudo systemctl disable dnsmasq 2>/dev/null || true

# Restore original dhcpcd.conf if backup exists
if [[ -f /etc/dhcpcd.conf.backup ]]; then
    echo "Restoring original dhcpcd configuration..."
    sudo cp /etc/dhcpcd.conf.backup /etc/dhcpcd.conf
fi

# Configure wpa_supplicant for client mode
echo "Configuring wpa_supplicant..."
sudo tee /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null <<EOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="$SSID"
    psk="$PASSPHRASE"
}
EOF

# Enable wpa_supplicant service
sudo systemctl enable wpa_supplicant

echo "WiFi client configuration complete!"
echo "Connected to: $SSID"
echo ""
echo "Please reboot the system to activate WiFi client mode:"
echo "sudo reboot"
echo ""
echo "After reboot, check your connection with:"
echo "iwgetid"
echo "ip addr show wlan0"