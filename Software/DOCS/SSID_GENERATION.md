# HoloBox SSID Generation

## Overview

The HoloBox system now generates unique, memorable SSIDs based on the device's MAC address, following the format `openUC2-NAME1-NAME2`.

## SSID Format

- **Format**: `openUC2-ADJECTIVE-NOUN`
- **Example**: `openUC2-Focus-Lens`, `openUC2-Digital-Scope`, `openUC2-Clear-Frame`
- **Combinations**: 1,056 possible unique combinations (32 adjectives × 33 nouns)

## How It Works

1. **MAC Address Detection**: The system reads the MAC address from the `wlan0` interface
2. **Hash Generation**: A SHA256 hash is created from the MAC address for even distribution
3. **Dictionary Lookup**: The hash is used to select an adjective and noun from predefined lists
4. **SSID Construction**: The final SSID is built as `openUC2-{ADJECTIVE}-{NOUN}`

## Implementation

### Files Modified
- `Software/setup_access_point.sh` - Updated to use MAC-based SSID generation
- `.github/workflows/build-sd-image.yml` - Embedded SSID generator in SD image build
- `Software/setup_holobox_image.sh` - Updated documentation references

### New Files Added
- `Software/generate_ssid.py` - Main SSID generator script
- `Software/test_ssid_generation.py` - Test suite for SSID functionality
- `Software/demo_ssid_generation.py` - Demo showing various SSID examples

## Benefits

1. **IPv4/IPv6 Compatibility**: Addresses university network IPv6 issues mentioned in #26
2. **Unique Identification**: Each Raspberry Pi gets a unique, deterministic SSID
3. **Memorable Names**: Human-readable names are easier to identify than random numbers
4. **Consistent**: Same MAC address always generates the same SSID
5. **OpenUC2 Branding**: All SSIDs clearly identify as openUC2 devices

## Testing

Run the test suite to verify functionality:
```bash
cd Software
python3 test_ssid_generation.py
```

## Example Usage

Generate SSID for current device:
```bash
cd Software
python3 generate_ssid.py
```

Generate SSID for specific interface:
```bash
python3 generate_ssid.py eth0
```