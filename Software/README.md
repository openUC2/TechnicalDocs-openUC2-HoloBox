# HoloBox Camera Streaming and Processing

This reorganized software provides a streamlined FastAPI backend for camera streaming with real-time hologram processing using PyScript, plus **automatic startup and Access Point functionality**.

## Features

### FastAPI Backend (`streamlined_camera_api.py`)
- **MJPEG Streaming**: Real-time camera feed at `/stream`
- **JPEG Capture**: Single frame capture at `/snapshot`
- **Camera Control**: Set exposure time and gain via `/settings`
- **WiFi Management**: Scan networks, connect to WiFi, enable Access Point via `/wifi/*`
- **Static File Serving**: Hosts the web interface at `/static/`
- **Mock Camera Support**: Works without actual camera hardware for development

### Enhanced Web Interface (`static/index.html`)
- **Real-time Streaming**: Display live camera feed
- **PyScript Integration**: Client-side Python processing
- **Fresnel Propagation**: Real-time hologram reconstruction
- **Interactive Controls**: Adjustable parameters (wavelength, pixel size, distance)
- **WiFi Management**: Scan networks, connect to WiFi, enable Access Point
- **Dual Display**: Original stream and processed hologram side-by-side

### Autostart & Access Point Features
- **Systemd Service**: Automatic startup on boot
- **Access Point Mode**: Create WiFi hotspot for direct smartphone connection
- **WiFi Client Mode**: Connect to existing WiFi networks
- **Web-based Configuration**: Manage network settings through the web interface

## Quick Setup (Raspberry Pi)

### Complete Installation
```bash
cd Software
sudo bash setup_holobox.sh
```

This will:
- Install all dependencies
- Set up the camera service to autostart on boot
- Configure Access Point scripts
- Create system management commands

### Manual Network Configuration

#### Enable Access Point Mode
```bash
sudo bash /opt/holobox/setup_access_point.sh
sudo reboot
```

After reboot:
- SSID: `HoloBox-XXXXX` (where XXXXX is part of hostname)
- Password: `holobox123`
- Gateway IP: `192.168.4.1`
- Access camera at: `http://192.168.4.1:8000/static/`

#### Connect to Existing WiFi
```bash
sudo bash /opt/holobox/setup_wifi_client.sh --ssid "YourNetwork" --password "YourPassword"
sudo reboot
```

## Usage

### 1. Start the API Server

#### Development (Manual Start)
```bash
cd Software
python streamlined_camera_api.py
```
Server runs on `http://localhost:8000`

#### Production (Service)
```bash
sudo systemctl start holobox-camera.service    # Start now
sudo systemctl enable holobox-camera.service   # Enable autostart
```

#### HTTPS Server (for GitHub Pages integration)
First generate SSL certificates:
```bash
python generate_ssl_cert.py
```

Then start with SSL:
```bash
python streamlined_camera_api.py --ssl-keyfile ssl_certs/server.key --ssl-certfile ssl_certs/server.crt
```
Server runs on `https://localhost:8000`

**Note**: Self-signed certificates will show browser warnings. This is normal for development/testing.

### 2. Access Web Interface
- **Local**: Navigate to `http://localhost:8000/static/`
- **Network**: Navigate to `http://[device-ip]:8000/static/`
- **Access Point**: Navigate to `http://192.168.4.1:8000/static/`

### 3. WiFi Management
Use the web interface to:
- View current connection status
- Scan for available networks
- Connect to WiFi networks (requires reboot)
- Enable Access Point mode (requires reboot)

### 4. System Management
```bash
holobox-info                    # Show system status
sudo systemctl status holobox-camera.service  # Check service status
sudo tail -f /var/log/holobox/camera.log      # View logs
```

### 3. Cross-Origin Access (CORS)
The server now supports CORS (Cross-Origin Resource Sharing), allowing access from:
- Static file servers (like VS Code Live Server)
- GitHub Pages
- Other domains

In the web interface, set the API URL to point to your server (e.g., `https://localhost:8000`).

### 4. Camera Controls
- **Start Stream**: Begin camera streaming
- **Stop Stream**: Stop camera streaming  
- **Set Exposure**: Adjust camera exposure time (microseconds)
- **Set Gain**: Adjust analogue gain
- **Capture**: Take single JPEG snapshot

### 5. Hologram Processing
- **Wavelength**: Adjust laser wavelength (380-700 nm)
- **Pixel Size**: Set camera pixel size (0.5-5.0 µm)
- **Distance**: Set propagation distance (0.1-20.0 mm)
- **Enable Processing**: Toggle real-time Fresnel propagation
- **Process Frame**: Process current frame once

## Technical Implementation

### Fresnel Propagation Algorithm
The implementation uses the angular spectrum method:
1. Convert input image to amplitude field
2. Apply 2D Fourier transform
3. Multiply by Fresnel kernel: `H = exp(i*2π/λ*z) * exp(i*π*λ*z*(fx²+fy²))`
4. Apply inverse Fourier transform
5. Calculate intensity for display

### API Endpoints
- `GET /`: Server status
- `GET /stream`: MJPEG video stream
- `GET /snapshot`: Single JPEG image
- `POST /settings`: Set camera parameters
- `GET /settings`: Get current parameters
- `GET /stats`: Image statistics

### Dependencies
- `fastapi`: Web API framework
- `uvicorn`: ASGI server
- `picamera2`: Raspberry Pi camera interface
- `numpy`: Numerical computations
- `opencv-python`: Image processing
- `pydantic`: Data validation

## Development Notes

- Mock camera implementation allows testing without hardware
- PyScript provides client-side scientific computing
- Processing parameters update in real-time
- Designed for minimal external dependencies
- Compatible with Raspberry Pi Zero deployment

## Testing

Run the validation script:
```bash
python test_implementation.py
```

This tests:
- Fresnel propagation mathematics
- API endpoint structure  
- HTML interface elements