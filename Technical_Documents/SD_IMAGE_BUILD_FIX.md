# SD Card Image Build Fixes

## Date: 2025-11-10

## Problems Identified

### 1. **WiFi Access Point Not Starting**
**Symptom:** No WiFi SSID visible after booting the flashed SD card.

**Root Cause:** 
- The `holobox-configure-ap` script was created but never executed
- `hostapd.conf` was never generated, causing `hostapd` service to fail
- No SSID was generated from the MAC address

**Fix:**
- Added execution of `holobox-configure-ap` to the `holobox-hotspot.service` systemd unit
- Added proper logging and error handling to `holobox-configure-ap`
- Added wait loop for wlan0 interface to be available (up to 10 seconds)
- Improved timing in the hotspot service initialization

### 2. **No Login Prompt on HDMI Console**
**Symptom:** After booting, the HDMI display shows no login prompt.

**Root Cause:** 
- Auto-login configuration was incomplete
- Getty service not properly configured for Raspberry Pi OS Bookworm

**Fix:**
- Enhanced auto-login configuration for `getty@tty1.service`
- Added auto-login configuration for serial console (for debugging)
- Added better systemd service dependencies

### 3. **NetworkManager Interference**
**Symptom:** NetworkManager could interfere with the WiFi AP configuration.

**Root Cause:**
- Incomplete NetworkManager configuration
- wlan0 interface could be managed by NetworkManager despite configuration

**Fix:**
- Enhanced NetworkManager configuration with main config file
- Improved unmanaged-devices configuration
- Better service ordering in systemd

## Changes Made

### Modified File: `.github/workflows/build-sd-image.yml`

#### 1. holobox-hotspot.service improvements:
```diff
+ After=network-online.target  # Changed from NetworkManager.service
+ Wants=network-online.target  # Changed from NetworkManager.service
+ ExecStart=/bin/bash -c 'sleep 2'  # Reduced from 4s and moved before nmcli
+ ExecStart=/bin/bash -c 'sleep 1'  # Added after nmcli
+ ExecStart=/usr/local/bin/holobox-configure-ap  # CRITICAL: Actually run the AP configuration
```

#### 2. holobox-configure-ap script improvements:
- Added logging to syslog for debugging
- Added wait loop for wlan0 interface availability
- Added informative echo messages for debugging
- Added error checking and exit codes
- Display SSID and password after configuration

#### 3. Auto-login configuration:
- Added serial console auto-login for debugging
- Improved comments and structure

#### 4. NetworkManager configuration:
- Added main `NetworkManager.conf` configuration
- Ensures `ifupdown` plugin is loaded
- Explicitly marks interfaces as unmanaged

#### 5. holobox-info improvements:
- Better formatted output with visual separators
- More comprehensive service status checks
- Added troubleshooting commands
- Automatically displayed on user login via `.bashrc`

## Testing Recommendations

After flashing the new image:

1. **Check boot messages:**
   ```bash
   sudo journalctl -b | grep holobox
   ```

2. **Verify services:**
   ```bash
   sudo systemctl status holobox-hotspot
   sudo systemctl status hostapd
   sudo systemctl status dnsmasq
   ```

3. **Check network configuration:**
   ```bash
   ip addr show wlan0
   iw dev wlan0 info
   cat /etc/holobox/ssid
   cat /etc/hostapd/hostapd.conf
   ```

4. **View service logs:**
   ```bash
   sudo journalctl -u holobox-hotspot -f
   sudo journalctl -u hostapd -f
   sudo journalctl -u dnsmasq -f
   ```

5. **Run info command:**
   ```bash
   holobox-info
   ```

## Expected Behavior After Fix

1. **On first boot:**
   - System generates unique SSID based on MAC address
   - WiFi AP starts automatically with SSID like `openUC2-Sharp-Lens`
   - Login prompt appears on HDMI console (auto-logged in as `pi`)
   - System information displayed automatically on login

2. **WiFi Access:**
   - SSID: `openUC2-[Adjective]-[Noun]` (unique per device)
   - Password: `holobox123`
   - AP IP: `192.168.4.1`

3. **SSH Access:**
   - User: `pi`
   - Password: `youseetoo`
   - Port: `22`

## Debugging if Issues Persist

If the WiFi still doesn't work:

```bash
# Check if wlan0 exists
ls -la /sys/class/net/

# Check NetworkManager status
sudo systemctl status NetworkManager
nmcli device status

# Manually test AP configuration
sudo /usr/local/bin/holobox-configure-ap

# Check rfkill
rfkill list
```

If auto-login doesn't work:

```bash
# Check getty service
sudo systemctl status getty@tty1

# Check for conflicting services
sudo systemctl list-units | grep getty

# View auto-login config
cat /etc/systemd/system/getty@tty1.service.d/autologin.conf
```

## Additional Notes

- The MAC-based SSID ensures each HoloBox has a unique identifier
- SSID is cached in `/etc/holobox/ssid` and persists across reboots
- All scripts log to syslog for easier debugging
- Service dependencies ensure proper startup order
