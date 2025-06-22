# HoloBox Software Documentation

This directory contains the software components for the HoloBox system, including camera interface, hologram processing, and xeus-lite JupyterLite notebook.

## Quick Start

### 1. xeus-lite JupyterLite Notebook

Build and run the xeus-lite Jupyter notebook with comprehensive hologram processing:

```bash
cd Software
python build_xeus_lite.py
python streamlined_camera_api.py
```

Open browser: `http://localhost:8000/static/notebook.html`

### 2. Camera Interface

Start the camera system:

```bash
python streamlined_camera_api.py
```

Access web interface: `http://localhost:8000/static/index.html`

## Components

### xeus-lite JupyterLite Notebook

- **Template**: Based on [xeus-lite-demo](https://github.com/jupyterlite/xeus-lite-demo)
- **Build Tool**: `build_xeus_lite.py` - CLI tool for building JupyterLite with xeus-python
- **Output**: Complete offline notebook in `static/jupyter/`
- **Features**: 
  - xeus-python kernel for full Python compatibility
  - Interactive hologram processing with widgets
  - Real-time camera integration
  - Advanced focus optimization algorithms
  - Complete offline operation
- **Documentation**: See `XEUS_LITE_README.md` for detailed information
- **Deployment**: Automatic deployment to `youseetoo.github.io/jupyter` via GitHub Actions

### Camera API

- **File**: `streamlined_camera_api.py` - FastAPI server for camera control
- **Features**: Live capture, parameter control, SSL support
- **Interface**: Web-based UI with real-time preview

## Detailed Usage

### xeus-lite Jupyter Notebook

The notebook provides a complete Python environment running in the browser with these features:

1. **Interactive Controls**: Real-time parameter adjustment via widgets
2. **Camera Integration**: Direct API calls to capture live holograms
3. **Advanced Processing**: Batch analysis, autofocus, and multi-distance reconstruction
4. **Visualization**: Multi-panel displays with various colormaps
5. **Export Functions**: Save results and parameters for analysis

### Camera System

#### Start the API Server

**Basic HTTP Server**:
```bash
cd Software
python streamlined_camera_api.py
```
Server runs on `http://localhost:8000`

**HTTPS Server** (for GitHub Pages integration):
```bash
python generate_ssl_cert.py  # Generate SSL certificates
python streamlined_camera_api.py --ssl-keyfile ssl_certs/server.key --ssl-certfile ssl_certs/server.crt
```
Server runs on `https://localhost:8000`

#### API Endpoints
- `GET /`: Server status
- `GET /stream`: MJPEG video stream
- `GET /snapshot`: Single JPEG image
- `POST /settings`: Set camera parameters
- `GET /settings`: Get current parameters
- `GET /stats`: Image statistics

#### Cross-Origin Access (CORS)
The server supports CORS, allowing access from GitHub Pages and other domains.

## GitHub Actions Deployment

The notebook is automatically deployed to `https://youseetoo.github.io/jupyter` when changes are pushed to the main branch. The workflow:

1. Installs JupyterLite dependencies
2. Builds the complete site with xeus-python kernel
3. Deploys to the specified GitHub Pages repository

## Dependencies

### Jupyter Notebook
- `jupyterlite-core>=0.2.0`
- `jupyterlite-xeus-python>=1.0.0`
- `numpy`, `matplotlib`, `scipy`
- `ipywidgets`, `pillow`, `requests`

### Camera API
- `fastapi`: Web API framework
- `uvicorn`: ASGI server
- `picamera2`: Raspberry Pi camera interface
- `numpy`: Numerical computations
- `opencv-python`: Image processing

## Development & Testing

Run validation scripts:
```bash
# Test camera API
python test_implementation.py

# Test Jupyter build
python test_jupyterlite_build.py
```

## File Structure

```
Software/
├── content/                          # Notebook content
│   └── hologram_processing.ipynb     # Main processing notebook
├── static/                          # Web assets
│   ├── jupyter/                     # Built JupyterLite site
│   ├── index.html                   # Camera interface
│   └── notebook.html               # Notebook entry point
├── build_xeus_lite.py              # Build script for xeus-lite
├── streamlined_camera_api.py       # Camera API server
├── XEUS_LITE_README.md            # Detailed notebook documentation
└── .github/workflows/
    └── deploy-jupyter.yml          # GitHub Actions deployment
```
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