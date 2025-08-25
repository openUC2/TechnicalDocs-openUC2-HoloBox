# HoloBox Camera Streaming and Processing

This reorganized software provides a streamlined FastAPI backend for camera streaming with real-time hologram processing using PyScript, plus **automatic startup and Access Point functionality**.


## Installation for Developers

***Attention: This will consume network traffic from your phone***

*Open the terminal and copy/paste the following items after logging into the raspi using the user credentials (e.g. pi/youseetoo)*


```
sudo apt-get update 
sudo apt-get install git python3-pip python3-picamera2 -y
sudo apt install -y libcap2-dev build-essential python3-dev
sudo apt install -y python3-libcamera libcamera-dev libcamera-apps
pip3 install --no-cache-dir --upgrade picamera2 --break-system-packages
git clone https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox/
cd TechnicalDocs-openUC2-HoloBox/Software
chmod +x setup_holobox.sh
# ./setup_holobox.sh
pip install -r requirements.txt --break-system-packages
```

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
- **Offline Compatibility**: All CSS/JS dependencies stored locally for use without internet
- **URL Redirection**: Root URL automatically redirects to the web interface
- **Hologram Processing**: Both PyScript (online) and JavaScript (offline) implementations
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

### Option 1: Pre-built SD Card Image (Recommended)

**🎉 New: Pre-built SD card images are now available!**

1. **Download** the latest image from [Releases](https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox/releases)
2. **Flash** the `.img.zip` file to an SD card (8GB+ recommended) using Raspberry Pi Imager
3. **Insert** the SD card into your Raspberry Pi and power on
4. **Connect** to WiFi network `HoloBox-XXXXX` (password: `holobox123`)
5. **Open browser** to `http://192.168.4.1:8000/static/`

**Features included in SD card image:**
- ✅ All software pre-installed and configured
- ✅ Works completely offline (no internet required)
- ✅ Automatic startup on boot
- ✅ Access Point mode ready to use
- ✅ Default credentials: SSH user `pi`, password `holobox123`

### Option 2: Manual Installation
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

### Educational Jupyter Notebook (`hologram_education_notebook.ipynb`)
- **Comprehensive Learning**: Step-by-step holography theory and implementation
- **Interactive Demonstrations**: Live parameter exploration with widgets
- **Live Camera Integration**: Connect to HoloBox API for real data processing
- **Hands-on Exercises**: Guided experiments for deeper understanding
- **Best Practices Guide**: Optimization tips and troubleshooting


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
- **Local**: Navigate to `http://localhost:8000/` (auto-redirects to interface)
- **Network**: Navigate to `http://[device-ip]:8000/` (auto-redirects to interface)
- **Access Point**: Navigate to `http://192.168.4.1:8000/` or `https://192.168.4.1:8000/`

**Note**: The root URL (`/`) automatically redirects to `/static/index.html` for user convenience.

### 3. Offline Functionality
The HoloBox web interface is fully functional without internet access:
- **Local Dependencies**: All CSS, JavaScript, and processing libraries are stored locally
- **Offline Processing**: JavaScript-based hologram processing when PyScript is unavailable
- **Complete Interface**: Full camera control and WiFi management work offline
- **Auto-redirect**: Convenient access via IP address alone

### 4. WiFi Management
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

### 

```
service holobox-camera status
sudo systemctl stop holobox-camera.service
```


### detect if camera is available 

```
vcgencmd get_camera
```


### Example for connecting to a network called "MyWiFi"

```
sudo nmtui
nmcli device wifi connect "openUC2" password "Wifi So You Can See Too"
```

```
● holobox-camera.service - HoloBox Camera API Server
     Loaded: loaded (/etc/systemd/system/holobox-camera.service; enabled; preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Wed 2025-07-30 09:01:30 CEST; 3s ago
    Process: 2428 ExecStart=python /opt/holobox/streamlined_camera_api.py --host 0.0.0.0 --port 8000 (code=exited, status=1/FAILURE)
   Main PID: 2428 (code=exited, status=1/FAILURE)
        CPU: 6.559s
```
# Show only whether the service is active
systemctl is-active holobox-camera.service

### 3. Use Educational Jupyter Notebook
For educational purposes and detailed learning:
```bash
# Install notebook dependencies
pip install -r notebook_requirements.txt

# Start Jupyter Notebook
jupyter notebook hologram_education_notebook.ipynb
```
See `NOTEBOOK_README.md` for detailed instructions.

### 4. Cross-Origin Access (CORS)
The server now supports CORS (Cross-Origin Resource Sharing), allowing access from:
- Static file servers (like VS Code Live Server)
- GitHub Pages
- Other domains

In the web interface, set the API URL to point to your server (e.g., `https://localhost:8000`).

### 5. Camera Controls
- **Start Stream**: Begin camera streaming
- **Stop Stream**: Stop camera streaming  
- **Set Exposure**: Adjust camera exposure time (microseconds)
- **Set Gain**: Adjust analogue gain
- **Capture**: Take single JPEG snapshot

### 6. Hologram Processing
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

#### SD Card Images

For the easiest setup, use the pre-built SD card images from the [Releases](https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox/releases) section. These include all dependencies pre-installed and work offline.

**Building SD Card Images:**
- See `Scripts/README.md` for detailed build instructions
- Automated builds via GitHub Actions on new releases
- Local builds supported with `Scripts/build_sd_image.sh`

#### Core API Server
- `fastapi`: Web API framework
- `uvicorn`: ASGI server
- `picamera2`: Raspberry Pi camera interface
- `numpy`: Numerical computations
- `opencv-python`: Image processing
- `pydantic`: Data validation

#### Educational Notebook
- `jupyter`: Interactive computing environment
- `ipywidgets`: Interactive widgets for notebooks
- `matplotlib`: Plotting and visualization
- `requests`: HTTP client library
- `Pillow`: Image processing library

## File Structure

```
Software/
├── streamlined_camera_api.py          # Main FastAPI server
├── hologram_education_notebook.ipynb  # Educational Jupyter notebook
├── static/                            # Web interface files
│   ├── index.html                     # PyScript-based web interface
│   ├── hologram_processing.py         # Client-side processing code
│   └── camera_controls.js             # JavaScript camera controls
├── requirements.txt                   # API server dependencies
├── notebook_requirements.txt          # Notebook dependencies  
├── validate_notebook.py               # Notebook validation script
├── README.md                         # This file
└── NOTEBOOK_README.md                # Detailed notebook documentation
```

## Development Notes

- Mock camera implementation allows testing without hardware
- PyScript provides client-side scientific computing
- Processing parameters update in real-time
- Designed for minimal external dependencies
- Compatible with Raspberry Pi Zero deployment

## Testing

### API Server Testing
Run the validation script:
```bash
python test_implementation.py
```

This tests:
- Fresnel propagation mathematics
- API endpoint structure  
- HTML interface elements

### Notebook Testing
Validate the notebook functionality:
```bash
python validate_notebook.py
```

This tests:
- Required dependencies
- Core hologram processing algorithms
- Synthetic hologram generation
- API connection functionality

## Educational Use

The Jupyter notebook is designed for:
- **Physics Education**: Understanding wave optics and diffraction
- **Research Training**: Learning digital holography techniques  
- **Engineering Courses**: Optical system design and analysis
- **Self-directed Learning**: Exploring holography interactively

Key educational features:
- Step-by-step theory explanations
- Interactive parameter exploration
- Real-time processing with live camera
- Hands-on exercises and experiments
- Best practices and optimization guides
