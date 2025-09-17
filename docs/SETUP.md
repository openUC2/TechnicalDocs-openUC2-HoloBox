# HoloBox Quick Start Guide

## Overview

The HoloBox provides a complete digital holographic imaging system with a web-based interface for camera control and real-time hologram processing.

## Power Requirements

**Important**: Pack **2× USB power supplies** into the box. The camera and accessories have high power draw requirements that cannot be met by a single USB supply.

## Network Access

### WiFi Connection

**SSID**: `openUC2-ULTRA-VIEW`  
**Password**: `holobox123`

### SSH Access

**Username**: `pi`  
**Password**: `youseetoo`

### Web Interface

**URL**: `http://192.168.4.1/`

> **Note**: The service runs on HTTP only via **port 80** (no `:8001` port suffix needed).

## Getting Started

1. **Power On**: Connect both USB power supplies to ensure stable operation.

2. **Connect to WiFi**: Join the `openUC2-ULTRA-VIEW` network using the password `holobox123`.

3. **Open Web Interface**: Navigate to `http://192.168.4.1/` in your web browser.

4. **Start Camera Stream**: Click "Start Stream" in the Camera Controls panel.

5. **Adjust Settings**: Use the camera controls to optimize exposure, white balance, and resolution.

6. **Process Holograms**: Configure hologram processing parameters and enable real-time processing.

## Browser Compatibility

### Desktop Browsers
- **Chrome**: Full compatibility (Windows/macOS/Linux)
- **Firefox**: Full compatibility (Windows/macOS/Linux)
- **Safari**: Full compatibility (macOS)

### Mobile/Tablet
- **iPad Safari**: Full compatibility
- **Android Chrome**: Full compatibility
- **iPhone Safari**: Full compatibility

### Troubleshooting iPad/Safari

If the video stream doesn't start automatically on iPad:

1. Tap the stream area to trigger a user gesture
2. Check that you're connected to the correct WiFi network
3. Ensure the URL is `http://` (not `https://`)
4. Refresh the page if controls appear collapsed

## Camera Controls

### Stream Controls
- **Start/Stop Stream**: Control live video feed
- **Capture JPEG**: Take single frame snapshots
- **Resolution**: Select from VGA (640×480) to Full HD (1920×1080)

### Exposure Control
- **Auto Exposure**: Automatic exposure control (default)
- **Manual Exposure**: Set specific exposure time (µs) and analogue gain
- Range: 1µs to 1,000,000µs exposure, 1.0× to 16.0× gain

### White Balance
- **Auto White Balance**: Automatic color balance (default)
- **Manual White Balance**: Set red and blue gain values
- Range: 0.0 to 8.0 for both red and blue gains

### Image Processing
- **Color Modes**: RGB, Grayscale, or individual R/G/B channels
- **Orientation**: Flip horizontal/vertical, rotate 0°/90°/180°/270°
- **ROI Processing**: Select region of interest for hologram processing

## Network Management

### Switching Networks

The HoloBox can connect to existing WiFi networks:

1. Open the **WiFi Management** panel
2. Click **"Scan Networks"** to see available networks
3. Enter network credentials in the connection form
4. Click **"Connect"** (requires reboot to take effect)

### Access Point Mode

To return to access point mode:

1. Click **"Enable Access Point"** in WiFi Management
2. Reboot the system when prompted

## Hologram Processing

### Parameters
- **Wavelength**: 380-700nm (default: 440nm blue light)
- **Pixel Size**: 0.5-5.0µm (default: 1.4µm)  
- **Distance**: 0.0-5.0mm propagation distance

### Controls
- **Enable Processing**: Start real-time hologram reconstruction
- **Process Current Frame**: Single frame processing
- **Debug Mode**: Show processing information

## System Information

### Network Details
- **Default IP**: 192.168.4.1 (Access Point mode)
- **Service Port**: 80 (HTTP only)
- **SSH Port**: 22 (standard)

### Performance
- **Stream Rate**: ~20 FPS MJPEG
- **Latency**: Depends on network conditions and Pi hardware
- **Resolution**: Up to 1920×1080 (hardware dependent)

## Troubleshooting

### Common Issues

**Stream won't start**:
- Check network connection to `openUC2-ULTRA-VIEW`
- Verify URL is `http://192.168.4.1/` (HTTP, not HTTPS)
- Try refreshing the page

**Controls not responding**:
- Check browser compatibility (use Chrome/Firefox for best results)
- Clear browser cache and reload
- Ensure JavaScript is enabled

**Poor stream quality**:
- Adjust resolution settings
- Check lighting conditions
- Verify power supply connections

**iPad/Safari specific**:
- Tap the video area to start stream (user gesture required)
- Check network settings in iPad WiFi preferences
- Try closing and reopening Safari

### Performance Optimization

**For better stream performance**:
- Use lower resolutions (640×480) for smoother frame rates
- Ensure both power supplies are connected
- Position device closer to HoloBox for better WiFi signal

**For better hologram quality**:
- Use higher resolutions (1280×720 or above)
- Adjust exposure for optimal lighting
- Fine-tune wavelength and pixel size parameters

## Support

For technical support and documentation:
- Check the main repository: `openUC2/TechnicalDocs-openUC2-HoloBox`
- Review issue tracker for known problems
- Consult technical documentation in the `Technical_Documents` directory