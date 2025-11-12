# HoloBox SD Image Testing Checklist

## Pre-Build Checklist

- [ ] All source files in `Software/` directory are up to date
- [ ] GitHub Actions workflow is the latest version
- [ ] No uncommitted changes in the repository

## Build Verification

- [ ] GitHub Actions workflow completed successfully
- [ ] Image artifact was created (check Actions artifacts)
- [ ] Image file size is reasonable (~2-4 GB compressed)

## Post-Flash Testing (Physical Hardware)

### Initial Boot (First Time)

- [ ] **Boot Process**
  - [ ] SD card inserted into Raspberry Pi
  - [ ] Power connected
  - [ ] Green LED blinks (SD card activity)
  - [ ] Boot completes within 60-90 seconds

- [ ] **HDMI Display**
  - [ ] Console output visible during boot
  - [ ] Login prompt appears automatically
  - [ ] User is auto-logged in as `pi`
  - [ ] HoloBox information banner is displayed
  - [ ] No error messages visible

- [ ] **WiFi Access Point**
  - [ ] SSID appears in WiFi scan: `openUC2-[Word]-[Word]`
  - [ ] SSID is unique (based on MAC address)
  - [ ] Can connect with password: `holobox123`
  - [ ] IP address `192.168.4.1` is reachable
  - [ ] Web interface accessible at `http://192.168.4.1/`

### SSH Access

- [ ] **SSH Connection**
  ```bash
  ssh pi@192.168.4.1
  # Password: youseetoo
  ```
  - [ ] SSH connection successful
  - [ ] HoloBox info banner displayed on login
  - [ ] User has sudo access

### Service Status

Run these commands after SSH login:

```bash
# Check all HoloBox services
sudo systemctl status holobox-hotspot
sudo systemctl status hostapd
sudo systemctl status dnsmasq
sudo systemctl status holobox-camera
sudo systemctl status nftables

# Run info command
holobox-info
```

- [ ] **holobox-hotspot.service**
  - [ ] Status: `active (exited)`
  - [ ] No errors in logs
  - [ ] wlan0 has IP `192.168.4.1/24`

- [ ] **hostapd.service**
  - [ ] Status: `active (running)`
  - [ ] SSID is broadcasting
  - [ ] Configuration file exists: `/etc/hostapd/hostapd.conf`

- [ ] **dnsmasq.service**
  - [ ] Status: `active (running)`
  - [ ] DHCP is assigning IPs in range `192.168.4.2-192.168.4.200`

- [ ] **holobox-camera.service**
  - [ ] Status: `active (running)`
  - [ ] Camera API is accessible on port 80
  - [ ] No errors in `/var/log/holobox/camera.log`

- [ ] **nftables.service**
  - [ ] Status: `active (exited)`
  - [ ] IP forwarding is enabled

### Network Configuration

```bash
# Check interfaces
ip addr show wlan0
ip addr show eth0

# Check WiFi
iw dev wlan0 info

# Check SSID file
cat /etc/holobox/ssid

# Check routing
ip route
```

- [ ] **wlan0**
  - [ ] IP: `192.168.4.1/24`
  - [ ] State: `UP`
  - [ ] SSID matches `/etc/holobox/ssid`

- [ ] **eth0** (if connected)
  - [ ] Has valid IP (DHCP or static)
  - [ ] Can reach internet (test: `ping 8.8.8.8`)

### Camera API Testing

From a client device connected to HoloBox WiFi:

```bash
# Test API endpoints
curl http://192.168.4.1/
curl http://192.168.4.1/api/health
```

- [ ] **Web Interface**
  - [ ] Opens in browser: `http://192.168.4.1/`
  - [ ] HTML page loads correctly
  - [ ] No 404 errors

- [ ] **Camera API**
  - [ ] Health endpoint responds
  - [ ] Camera controls work
  - [ ] Image capture works

### Log Review

```bash
# View system logs
sudo journalctl -b | grep -i error
sudo journalctl -b | grep -i fail

# View HoloBox specific logs
sudo journalctl -u holobox-hotspot
sudo journalctl -u hostapd
sudo journalctl -u dnsmasq
sudo journalctl -u holobox-camera

# Check for AP configuration logs
sudo journalctl | grep holobox-configure-ap
```

- [ ] No critical errors in system logs
- [ ] AP configuration completed successfully
- [ ] All services started without errors

### Reboot Testing

```bash
sudo reboot
```

- [ ] **After Reboot**
  - [ ] All services start automatically
  - [ ] WiFi AP is available
  - [ ] Same SSID is used (cached)
  - [ ] Auto-login still works
  - [ ] Camera service starts

### Client Device Testing

Test from multiple devices:

- [ ] **Laptop/PC**
  - [ ] Can connect to WiFi
  - [ ] Can access web interface
  - [ ] Can ping `192.168.4.1`

- [ ] **Smartphone**
  - [ ] Can connect to WiFi
  - [ ] Can access web interface in mobile browser

- [ ] **Multiple Clients**
  - [ ] 2+ devices can connect simultaneously
  - [ ] DHCP assigns different IPs
  - [ ] Both can access services

### Internet Sharing (if eth0 connected)

With Ethernet cable connected:

```bash
# On HoloBox
ping 8.8.8.8

# Check NAT
sudo nft list ruleset
```

- [ ] HoloBox can reach internet via eth0
- [ ] NAT is configured
- [ ] WiFi clients can reach internet through HoloBox

### File System Check

```bash
# Check installation
ls -la /opt/holobox/
ls -la /usr/local/bin/holobox-*
ls -la /etc/holobox/
ls -la /etc/systemd/system/holobox-*

# Check configurations
cat /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf
cat /etc/dnsmasq.d/holobox-ap.conf
cat /etc/nftables.conf
```

- [ ] All HoloBox files are present
- [ ] Scripts are executable
- [ ] Configurations are correct

## Regression Testing

Test that previous functionality still works:

- [ ] Camera functionality unchanged
- [ ] Web interface features work
- [ ] No new errors introduced

## Performance Testing

- [ ] Boot time < 90 seconds
- [ ] WiFi connection time < 10 seconds
- [ ] Web page load time < 3 seconds
- [ ] Camera response time acceptable

## Documentation

- [ ] Update `README.md` with new SSID format if needed
- [ ] Update user documentation
- [ ] Document any known issues
- [ ] Update changelog

## Sign-Off

**Tester Name:** _________________  
**Date:** _________________  
**Image Version:** _________________  
**Result:** ☐ PASS ☐ FAIL ☐ PARTIAL  

**Notes:**
```
(Add any additional observations or issues found during testing)
```

---

## Quick Test Commands

Copy-paste these for quick testing:

```bash
# Service status
sudo systemctl status holobox-hotspot hostapd dnsmasq holobox-camera nftables --no-pager

# Network info
ip addr show wlan0; iw dev wlan0 info; cat /etc/holobox/ssid

# Logs
sudo journalctl -u holobox-hotspot -u hostapd -u dnsmasq --no-pager -n 50

# HoloBox info
holobox-info
```
