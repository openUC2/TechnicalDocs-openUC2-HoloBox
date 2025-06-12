# HoloBox Camera Streaming and Processing

This reorganized software provides a streamlined FastAPI backend for camera streaming with real-time hologram processing using PyScript.

## Features

### FastAPI Backend (`streamlined_camera_api.py`)
- **MJPEG Streaming**: Real-time camera feed at `/stream`
- **JPEG Capture**: Single frame capture at `/snapshot`
- **Camera Control**: Set exposure time and gain via `/settings`
- **Static File Serving**: Hosts the web interface at `/static/`
- **Mock Camera Support**: Works without actual camera hardware for development

### Enhanced Web Interface (`static/index.html`)
- **Real-time Streaming**: Display live camera feed
- **PyScript Integration**: Client-side Python processing
- **Fresnel Propagation**: Real-time hologram reconstruction
- **Interactive Controls**: Adjustable parameters (wavelength, pixel size, distance)
- **Dual Display**: Original stream and processed hologram side-by-side

## Usage

### 1. Start the API Server
```bash
cd Software
python streamlined_camera_api.py
```
Server runs on `http://localhost:8000`

### 2. Access Web Interface
Navigate to `http://localhost:8000/static/` in your browser

### 3. Camera Controls
- **Start Stream**: Begin camera streaming
- **Stop Stream**: Stop camera streaming  
- **Set Exposure**: Adjust camera exposure time (microseconds)
- **Set Gain**: Adjust analogue gain
- **Capture**: Take single JPEG snapshot

### 4. Hologram Processing
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