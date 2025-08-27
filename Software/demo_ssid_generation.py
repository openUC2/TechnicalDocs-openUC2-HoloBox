#!/usr/bin/env python3
"""
Demo script showing SSID generation for different MAC addresses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_ssid import mac_to_indices, ADJECTIVES, NOUNS

def demo_ssid_generation():
    """Demonstrate SSID generation for various MAC addresses"""
    print("HoloBox SSID Generation Demo")
    print("=" * 40)
    print("Format: openUC2-ADJECTIVE-NOUN")
    print("Based on MAC address hash lookup")
    print()
    
    # Test with some example MAC addresses
    test_macs = [
        "b8:27:eb:12:34:56",  # Typical Raspberry Pi MAC prefix
        "dc:a6:32:ab:cd:ef",  # Another common prefix
        "00:11:22:33:44:55",  # Generic example
        "aa:bb:cc:dd:ee:ff",  # Another example
        "b8:27:eb:98:76:54",  # Another Pi MAC
    ]
    
    print("Example SSID generations:")
    print("-" * 40)
    
    for mac in test_macs:
        adj_idx, noun_idx = mac_to_indices(mac)
        adjective = ADJECTIVES[adj_idx]
        noun = NOUNS[noun_idx]
        ssid = f"openUC2-{adjective}-{noun}"
        print(f"MAC: {mac} → {ssid}")
    
    print()
    print(f"Dictionary sizes:")
    print(f"- Adjectives: {len(ADJECTIVES)} options")
    print(f"- Nouns: {len(NOUNS)} options") 
    print(f"- Total combinations: {len(ADJECTIVES) * len(NOUNS):,}")
    print()
    print("This provides a good distribution of unique, memorable SSID names!")

if __name__ == "__main__":
    demo_ssid_generation()