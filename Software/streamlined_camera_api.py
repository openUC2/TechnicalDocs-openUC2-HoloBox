"""
Streamlined FastAPI service for Raspberry Pi camera with hologram processing support
- MJPEG streaming
- JPEG capture  
- Camera parameter control (exposure, gain)
- Static file serving for web interface
- Uses only picamera2 interface
"""

from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2
import time
import uvicorn
import os

# Mock picamera2 for development/testing environments
try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
except ImportError:
    print("Warning: picamera2 not available, using mock camera")
    CAMERA_AVAILABLE = False
    
    class MockPicamera2:
        def __init__(self):
            self.frame_counter = 0
            
        def create_video_configuration(self, **kwargs):
            return {}
            
        def configure(self, config):
            pass
            
        def start(self):
            pass
            
        def capture_request(self):
            return MockRequest()
            
        def set_controls(self, controls):
            print(f"Mock: Setting controls {controls}")
            
        def capture_metadata(self):
            return {"ExposureTime": 10000, "AnalogueGain": 1.0}
    
    class MockRequest:
        def make_array(self, name):
            # Create a mock camera frame with some pattern
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            # Add some pattern for testing
            cv2.circle(frame, (320, 240), 50, (255, 255, 255), -1)
            return frame
            
        def release(self):
            pass
    
    Picamera2 = MockPicamera2

app = FastAPI(title="Streamlined Camera API", description="Camera streaming and processing API")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize camera
if CAMERA_AVAILABLE:
    picam = Picamera2()
    picam.configure(picam.create_video_configuration(main={"size": (640, 480)}))
    picam.start()
else:
    picam = MockPicamera2()

# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Models
class CameraSettings(BaseModel):
    exposure_us: int | None = None   # microseconds
    gain: float | None = None        # analogue gain

class WiFiConfig(BaseModel):
    ssid: str
    password: str | None = None

# Utility functions
def _capture() -> np.ndarray:
    """Capture a frame from the camera"""
    if CAMERA_AVAILABLE:
        req = picam.capture_request()
        arr = req.make_array("main")
        req.release()
        return arr
    else:
        return picam.capture_request().make_array("main")

def _jpeg(frame: np.ndarray) -> bytes:
    """Encode frame as JPEG"""
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return buf.tobytes()

# API Endpoints
@app.get("/")
def root():
    return {"message": "Streamlined Camera API", "camera_available": CAMERA_AVAILABLE}

@app.get("/snapshot", summary="Single JPEG frame")
def snapshot() -> Response:
    """Get a single JPEG image from the camera"""
    img = _jpeg(_capture())
    return Response(content=img, media_type="image/jpeg")

@app.get("/stream", summary="MJPEG stream")
def stream():
    """Get continuous MJPEG stream"""
    boundary = b"frame"
    def gen():
        while True:
            yield (
                b"--" + boundary +
                b"\r\nContent-Type: image/jpeg\r\n\r\n" +
                _jpeg(_capture()) + b"\r\n"
            )
            time.sleep(0.05)  # ~20 FPS
    return StreamingResponse(
        gen(),
        media_type=f"multipart/x-mixed-replace; boundary={boundary.decode()}",
    )

@app.post("/settings", summary="Set camera parameters")
def set_settings(s: CameraSettings):
    """Set camera exposure and/or gain"""
    controls = {}
    if s.exposure_us is not None:
        controls["ExposureTime"] = int(s.exposure_us)
    if s.gain is not None:
        controls["AnalogueGain"] = float(s.gain)
    if not controls:
        raise HTTPException(400, "No parameters supplied")
    
    if CAMERA_AVAILABLE:
        picam.set_controls(controls)
    else:
        print(f"Mock: Would set controls {controls}")
    
    return controls

@app.get("/settings", summary="Get current camera parameters")
def get_settings():
    """Get current camera exposure and gain"""
    if CAMERA_AVAILABLE:
        md = picam.capture_metadata()
        return {
            "exposure_us": md.get("ExposureTime"),
            "gain": md.get("AnalogueGain"),
        }
    else:
        return {"exposure_us": 10000, "gain": 1.0}

@app.get("/stats", summary="Image statistics")
def stats():
    """Get min/max/mean pixel values of current frame"""
    img = _capture()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return {
        "min": int(np.min(gray)),
        "max": int(np.max(gray)),
        "mean": float(np.mean(gray)),
    }

# WiFi Management Endpoints
@app.get("/wifi/status", summary="Get WiFi status")
def get_wifi_status():
    """Get current WiFi connection status and available networks"""
    import subprocess
    
    try:
        # Get current connection
        current = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
        connected_ssid = current.stdout.strip() if current.returncode == 0 else None
        
        # Get IP address
        ip_result = subprocess.run(["ip", "addr", "show", "wlan0"], capture_output=True, text=True)
        ip_address = None
        if ip_result.returncode == 0:
            for line in ip_result.stdout.split('\n'):
                if 'inet ' in line and not '127.0.0.1' in line:
                    ip_address = line.strip().split()[1].split('/')[0]
                    break
        
        # Check if running as access point
        hostapd_status = subprocess.run(["systemctl", "is-active", "hostapd"], capture_output=True, text=True)
        is_access_point = hostapd_status.stdout.strip() == "active"
        
        return {
            "connected_ssid": connected_ssid,
            "ip_address": ip_address,
            "is_access_point": is_access_point,
            "interface": "wlan0"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/wifi/scan", summary="Scan for available networks")
def scan_wifi():
    """Scan for available WiFi networks"""
    import subprocess
    
    try:
        # Trigger scan
        subprocess.run(["sudo", "iwlist", "wlan0", "scan"], capture_output=True)
        
        # Get scan results
        result = subprocess.run(["sudo", "iwlist", "wlan0", "scan"], capture_output=True, text=True)
        
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'Cell ' in line and 'Address:' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {"bssid": line.split('Address: ')[1]}
            elif 'ESSID:' in line:
                essid = line.split('ESSID:')[1].strip('"')
                if essid:
                    current_network["ssid"] = essid
            elif 'Quality=' in line:
                try:
                    quality = line.split('Quality=')[1].split(' ')[0]
                    current_network["quality"] = quality
                except:
                    pass
            elif 'Encryption key:' in line:
                encrypted = 'on' in line
                current_network["encrypted"] = encrypted
        
        if current_network:
            networks.append(current_network)
        
        # Remove duplicates and filter out networks without SSID
        unique_networks = []
        seen_ssids = set()
        for network in networks:
            if 'ssid' in network and network['ssid'] not in seen_ssids:
                seen_ssids.add(network['ssid'])
                unique_networks.append(network)
        
        return {"networks": unique_networks}
    except Exception as e:
        return {"error": str(e)}

@app.post("/wifi/connect", summary="Connect to WiFi network")
def connect_wifi(config: WiFiConfig):
    """Connect to a WiFi network (switches from AP mode to client mode)"""
    import subprocess
    import os
    
    try:
        # Call the WiFi client setup script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_wifi_client.sh")
        
        if config.password:
            cmd = [script_path, "--ssid", config.ssid, "--password", config.password]
        else:
            return {"error": "Password is required"}
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {
                "status": "success", 
                "message": f"WiFi configuration updated for {config.ssid}. Reboot required.",
                "ssid": config.ssid
            }
        else:
            return {"error": f"Configuration failed: {result.stderr}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/wifi/access_point", summary="Enable Access Point mode")
def enable_access_point():
    """Enable Access Point mode"""
    import subprocess
    import os
    
    try:
        # Call the access point setup script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_access_point.sh")
        
        result = subprocess.run([script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            return {
                "status": "success", 
                "message": "Access Point configured. Reboot required.",
                "output": result.stdout
            }
        else:
            return {"error": f"Access Point setup failed: {result.stderr}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Streamlined Camera API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind to")
    parser.add_argument("--ssl-keyfile", help="SSL private key file")
    parser.add_argument("--ssl-certfile", help="SSL certificate file")
    args = parser.parse_args()
    
    # Configure SSL if certificates provided
    ssl_kwargs = {}
    if args.ssl_keyfile and args.ssl_certfile:
        ssl_kwargs = {
            "ssl_keyfile": args.ssl_keyfile,
            "ssl_certfile": args.ssl_certfile
        }
        print(f"Starting server with SSL on https://{args.host}:{args.port}")
    else:
        print(f"Starting server on http://{args.host}:{args.port}")
        print("For SSL support, use --ssl-keyfile and --ssl-certfile arguments")
    
    uvicorn.run(app, host=args.host, port=args.port, **ssl_kwargs)