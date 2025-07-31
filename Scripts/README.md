# HoloBox SD Card Image Build System

This directory contains the automated build system for creating HoloBox SD card images based on Raspberry Pi OS Lite 64-bit.

## Overview

The build system creates a complete, ready-to-use SD card image that includes:
- Pre-installed HoloBox software and dependencies
- Automatic camera service startup on boot
- Access Point mode for direct smartphone connection
- Web interface for camera controls and WiFi management
- All Python dependencies pre-installed (works offline)

## Automated Building (GitHub Actions)

### Trigger Build

The SD card image is automatically built using GitHub Actions when:
1. **New Release**: Push a tag starting with 'v' (e.g., `v1.0.0`)
2. **Manual Trigger**: Use the workflow dispatch feature in GitHub Actions

```bash
# Create and push a new release tag
git tag v1.0.0
git push origin v1.0.0
```

### GitHub Actions Workflow

The workflow (`.github/workflows/build-sd-image.yml`) performs:
1. Downloads Raspberry Pi OS Lite 64-bit
2. Expands the image to accommodate HoloBox software
3. Sets up ARM64 emulation using QEMU
4. Mounts the image and sets up chroot environment
5. Installs HoloBox software and dependencies
6. Configures services for automatic startup
7. Compresses the final image
8. Uploads to GitHub Releases

### Download Pre-built Images

Pre-built images are available in the [Releases](https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox/releases) section.

## Local Building

### Prerequisites

For local building on Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y \
    qemu-user-static \
    binfmt-support \
    parted \
    zip \
    wget \
    xz-utils
```

### Build Process

1. **Clone the repository**:
   ```bash
   git clone https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox.git
   cd TechnicalDocs-openUC2-HoloBox
   ```

2. **Run the build script**:
   ```bash
   chmod +x Scripts/build_sd_image.sh
   ./Scripts/build_sd_image.sh
   ```

3. **Find the output**:
   The compressed image will be saved as `Scripts/holobox-sdcard-YYYYMMDD.img.zip`

### Build Script Features

- **Dependency checking**: Verifies all required tools are installed
- **Progress logging**: Color-coded output with timestamps
- **Error handling**: Automatic cleanup on failure
- **Resume capability**: Can resume if base image is already downloaded

## Image Contents

### Software Included

- **HoloBox Camera API**: FastAPI-based camera streaming server
- **Web Interface**: Complete web-based control interface
- **Python Environment**: Virtual environment with all dependencies
- **System Services**: Configured for automatic startup
- **Network Tools**: Access Point and WiFi client setup scripts

### Default Configuration

- **Username**: `pi`
- **Password**: `holobox123`
- **SSH**: Enabled with banner
- **Camera Service**: Auto-start on boot
- **Web Interface**: Available on port 8000
- **Access Point**: SSID `HoloBox-XXXXX`, password `holobox123`

### Directory Structure

```
/opt/holobox/                     # Main installation directory
├── venv/                         # Python virtual environment
├── static/                       # Web interface files
├── streamlined_camera_api.py     # Main camera server
├── setup_access_point.sh         # Access Point setup
├── setup_wifi_client.sh          # WiFi client setup
└── first-boot.sh                 # First boot configuration

/var/log/holobox/                 # Log files
└── camera.log                    # Camera service logs

/usr/local/bin/
└── holobox-info                  # System status script
```

## Using the SD Card Image

### Flashing the Image

1. **Download** the latest image from [Releases](https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox/releases)
2. **Extract** the `.img.zip` file
3. **Flash** using Raspberry Pi Imager, Etcher, or `dd`:
   ```bash
   # Using dd (replace /dev/sdX with your SD card device)
   sudo dd if=holobox-sdcard-YYYYMMDD.img of=/dev/sdX bs=4M status=progress
   ```

### First Boot

1. **Insert** the SD card into a Raspberry Pi 4
2. **Power on** the device
3. **Wait** for first boot initialization (filesystem expansion)
4. **Connect** to WiFi network `HoloBox-XXXXX` (password: `holobox123`)
5. **Open browser** to `http://192.168.4.1:8000/static/`

### WiFi Configuration

The image supports two network modes:

#### Access Point Mode (Default)
- Creates WiFi hotspot `HoloBox-XXXXX`
- Gateway IP: `192.168.4.1`
- Web interface: `http://192.168.4.1:8000/static/`

#### WiFi Client Mode
- Connect to existing WiFi networks
- Use web interface to scan and connect
- Access via device IP address

### System Management

```bash
# Check system status
holobox-info

# View service logs
sudo journalctl -u holobox-camera.service -f

# Start/stop/restart camera service
sudo systemctl start holobox-camera.service
sudo systemctl stop holobox-camera.service
sudo systemctl restart holobox-camera.service

# Switch to Access Point mode
sudo /opt/holobox/setup_access_point.sh

# Connect to WiFi network
sudo /opt/holobox/setup_wifi_client.sh --ssid "NetworkName" --password "password"
```

## Customization

### Modifying the Build

To customize the image build:

1. **Edit** `Software/setup_holobox_image.sh` for installation changes
2. **Modify** `.github/workflows/build-sd-image.yml` for build process changes
3. **Update** `Software/requirements.txt` for Python dependency changes

### Adding Software

Add custom software installation to `Software/setup_holobox_image.sh`:

```bash
# Install additional packages
apt-get install -y your-package

# Install Python packages
sudo -u pi /opt/holobox/venv/bin/pip install your-python-package
```

## Troubleshooting

### Build Issues

1. **Insufficient disk space**: Ensure 8GB+ free space
2. **Permission errors**: Run with user that has sudo access
3. **Loop device busy**: Reboot and try again
4. **QEMU issues**: Ensure `qemu-user-static` is installed

### Runtime Issues

1. **Service not starting**: Check logs with `journalctl -u holobox-camera.service`
2. **WiFi problems**: Verify wlan0 interface exists
3. **Web interface unreachable**: Check firewall settings
4. **Camera not detected**: Ensure camera is connected and enabled

### Log Locations

- **Camera service**: `/var/log/holobox/camera.log`
- **System logs**: `journalctl -u holobox-camera.service`
- **First boot**: `journalctl -u holobox-first-boot.service`

## Development

### Testing Changes

1. **Build locally** using `Scripts/build_sd_image.sh`
2. **Test in QEMU** or on actual hardware
3. **Validate** all services start correctly
4. **Check** web interface accessibility

### Contributing

1. **Fork** the repository
2. **Make changes** to build scripts or software
3. **Test** locally before submitting
4. **Submit** pull request with description

## Security Considerations

### Default Credentials

The image ships with default credentials for ease of use:
- SSH password: `holobox123`
- WiFi password: `holobox123`

**Important**: Change these passwords in production environments!

### Network Security

- SSH is enabled by default
- Access Point uses WPA2 security
- Web interface has no authentication (local network only)

### Recommendations

1. **Change default passwords** after first boot
2. **Disable SSH** if not needed
3. **Use firewall** in production environments
4. **Regular updates** of system packages

## License

This build system is part of the openUC2 HoloBox project. See the main repository LICENSE file for details.