# HoloBox Auto-Login Configuration

This document explains how the HoloBox SD card image is configured to automatically log in the `pi` user without prompting for username creation.

## Problem

When booting a fresh Raspberry Pi OS image, the system may prompt for username creation instead of using a pre-configured user. This creates a poor user experience for HoloBox users who expect the device to work immediately after flashing the SD card.

## Solution

The HoloBox implements a multi-layered approach to ensure reliable auto-login:

### 1. Build-Time Configuration

During SD card image creation, the build process:

- **Creates the pi user** with password `youseetoo`
- **Disables user setup services** (`userconfig`, `piwiz`) that prompt for username
- **Configures auto-login** at the system level
- **Creates userconf.txt** in the boot partition as a fallback
- **Enables SSH** for remote access

### 2. First-Boot Service

A dedicated systemd service (`holobox-user-setup.service`) runs on first boot to:

- **Verify pi user exists** and has correct configuration
- **Set up auto-login** for the console (tty1)
- **Disable any remaining setup wizards**
- **Configure the user environment** (SSH keys, bashrc, etc.)
- **Self-disable** after successful completion

### 3. Auto-Login Configuration

The auto-login is configured by modifying the getty service for tty1:

```ini
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
```

This ensures the pi user is automatically logged in when the system boots to the console.

## Implementation Details

### Service Definition

The first-boot service is defined in `/etc/systemd/system/holobox-user-setup.service`:

```ini
[Unit]
Description=HoloBox First Boot User Setup
After=systemd-user-sessions.service
Before=getty@tty1.service
DefaultDependencies=false

[Service]
Type=oneshot
ExecStart=/opt/holobox/setup-user-first-boot.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

### Setup Script

The setup script (`/opt/holobox/setup-user-first-boot.sh`) performs these actions:

1. **User Creation/Verification**
   - Creates pi user if it doesn't exist
   - Ensures user is in sudo group
   - Sets password to `youseetoo`

2. **Service Management**
   - Disables `userconfig.service`
   - Masks `piwiz.service`
   - Prevents first-time setup wizards

3. **Auto-Login Setup**
   - Creates getty override configuration
   - Enables auto-login for pi user

4. **Environment Setup**
   - Creates SSH key directory
   - Sets up bashrc with HoloBox welcome message
   - Ensures proper file ownership

5. **Self-Cleanup**
   - Disables itself after successful run
   - Creates completion marker file

## Testing

Use the provided test script to verify auto-login configuration:

```bash
sudo /opt/holobox/Scripts/test_auto_login.sh
```

This script checks:
- Pi user existence and configuration
- Auto-login service configuration
- First-boot service status
- Completion markers and logs

## Troubleshooting

### Issue: Still prompted for username

**Symptoms:** System asks "Please enter new username:" on first boot

**Causes:**
- First-boot service failed to run
- User creation failed during image build
- Auto-login configuration was overridden

**Solutions:**
1. Check service status: `systemctl status holobox-user-setup.service`
2. Review logs: `journalctl -u holobox-user-setup.service`
3. Check user setup log: `cat /var/log/holobox-user-setup.log`
4. Manually run setup: `sudo /opt/holobox/setup-user-first-boot.sh`

### Issue: Auto-login not working

**Symptoms:** System boots to login prompt instead of automatic login

**Solutions:**
1. Check getty configuration: `cat /etc/systemd/system/getty@tty1.service.d/autologin.conf`
2. Restart getty service: `sudo systemctl restart getty@tty1.service`
3. Verify pi user exists: `id pi`

### Issue: Permission denied

**Symptoms:** Cannot access files or run commands as pi user

**Solutions:**
1. Check user groups: `groups pi`
2. Verify sudo access: `sudo -l -U pi`
3. Fix ownership: `sudo chown -R pi:pi /home/pi`

## Logs and Diagnostics

- **Setup log:** `/var/log/holobox-user-setup.log` - First-boot setup details
- **Service status:** `systemctl status holobox-user-setup.service`
- **Getty status:** `systemctl status getty@tty1.service`
- **User info:** `getent passwd pi`

## Default Credentials

After successful setup:
- **Username:** `pi`
- **Password:** `youseetoo`
- **SSH Access:** Enabled by default
- **Sudo Access:** Enabled for pi user

## Security Considerations

The default password should be changed after initial setup for production use:

```bash
passwd pi
```

For automated deployments, consider using SSH keys instead of password authentication.