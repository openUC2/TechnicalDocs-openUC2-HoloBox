#!/usr/bin/env python3
"""
HoloBox SSID Generator
Generates unique SSID names based on MAC address using dictionary lookup
Format: openUC2-NAME1-NAME2
"""

import hashlib
import subprocess
import sys


# Name dictionaries for the lookup table
ADJECTIVES = [
    "Bright", "Clear", "Focus", "Sharp", "Zoom", "Light", "Flash", "Lens", 
    "Image", "Photo", "Pixel", "Frame", "View", "Scope", "Beam", "Wave",
    "Crystal", "Prism", "Filter", "Mirror", "Optic", "Laser", "Holo", "Ray",
    "Spectrum", "Digital", "Micro", "Macro", "Ultra", "Super", "Nano", "Mini"
]

NOUNS = [
    "Box", "Cam", "Lab", "Scope", "Lens", "Beam", "Wave", "Light", "Focus",
    "View", "Snap", "Shot", "Frame", "Pixel", "Image", "Photo", "Optic",
    "Prism", "Mirror", "Filter", "Ray", "Laser", "Holo", "Spectrum", "Micro",
    "Macro", "Unit", "Device", "System", "Tool", "Cube", "Capsule", "Pod"
]


def get_mac_address(interface='wlan0'):
    """Get MAC address of specified network interface"""
    try:
        # Try to read MAC from /sys/class/net
        with open(f'/sys/class/net/{interface}/address', 'r') as f:
            mac = f.read().strip()
            return mac
    except FileNotFoundError:
        try:
            # Fallback: try to get MAC using ip command
            result = subprocess.run(['ip', 'link', 'show', interface], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'link/ether' in line:
                        mac = line.split()[1]
                        return mac
        except Exception:
            pass
    
    # If all else fails, generate a fallback based on hostname
    try:
        result = subprocess.run(['hostname'], capture_output=True, text=True)
        hostname = result.stdout.strip()
        # Create a pseudo-MAC from hostname
        mac_hash = hashlib.md5(hostname.encode()).hexdigest()[:12]
        mac = ':'.join([mac_hash[i:i+2] for i in range(0, 12, 2)])
        return mac
    except Exception:
        # Ultimate fallback
        return "00:00:00:00:00:01"


def mac_to_indices(mac_address):
    """Convert MAC address to lookup table indices"""
    # Remove colons and convert to bytes
    mac_bytes = bytes.fromhex(mac_address.replace(':', ''))
    
    # Create hash for more even distribution
    hash_bytes = hashlib.sha256(mac_bytes).digest()
    
    # Use first 4 bytes to generate indices
    adj_index = (hash_bytes[0] << 8 | hash_bytes[1]) % len(ADJECTIVES)
    noun_index = (hash_bytes[2] << 8 | hash_bytes[3]) % len(NOUNS)
    
    return adj_index, noun_index


def generate_ssid(interface='wlan0'):
    """Generate SSID in format openUC2-NAME1-NAME2"""
    mac_address = get_mac_address(interface)
    adj_index, noun_index = mac_to_indices(mac_address)
    
    adjective = ADJECTIVES[adj_index]
    noun = NOUNS[noun_index]
    
    ssid = f"openUC2-{adjective}-{noun}"
    return ssid


def main():
    """Command line interface"""
    if len(sys.argv) > 1:
        interface = sys.argv[1]
    else:
        interface = 'wlan0'
    
    mac = get_mac_address(interface)
    ssid = generate_ssid(interface)
    
    print(f"Interface: {interface}")
    print(f"MAC Address: {mac}")
    print(f"Generated SSID: {ssid}")
    
    return ssid


if __name__ == "__main__":
    main()