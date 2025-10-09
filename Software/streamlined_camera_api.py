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
import subprocess
import sys

# Mock picamera2 for development/testing environments
try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
    picam = Picamera2()
    picam.configure(picam.create_video_configuration(main={"size": (640, 480)}))
    picam.start()    
except Exception as e:
    print(f"Warning: picamera2 not available, using mock camera. Error: {e}")
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
            cv2.rectangle(frame, (320, 240), (370, 290), (255, 255, 255), -1)
            return frame
            
        def release(self):
            pass
    
    picam = MockPicamera2()

app = FastAPI(title="Streamlined Camera API", description="Camera streaming and processing API")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Camera state tracking
camera_state = {
    "exposure_auto": True,
    "exposure_us": 10000,
    "analogue_gain": 1.0,
    "awb_auto": True,
    "awb_gains": {"red": 1.5, "blue": 1.5},
    "resolution": {"width": 640, "height": 480},
    "color_mode": "rgb",
    "streaming": False,
    "stream_config": None  # Store streaming configuration
}

# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# SSL certificate generation function
def generate_ssl_certificates_if_needed():
    """Generate self-signed SSL certificates if they don't exist"""
    cert_dir = "ssl_certs"
    keyfile = os.path.join(cert_dir, "server.key")
    certfile = os.path.join(cert_dir, "server.crt")
    
    # Check if certificates already exist
    if os.path.exists(keyfile) and os.path.exists(certfile):
        print(f"SSL certificates found in {cert_dir}/")
        return keyfile, certfile
    
    try:
        # Create certificate directory if it doesn't exist
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
        
        print("Generating SSL certificates for HTTPS support...")
        
        # Generate private key
        print("  Generating private key...")
        subprocess.run([
            "openssl", "genrsa", "-out", keyfile, "2048"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Generate certificate
        print("  Generating self-signed certificate...")
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", keyfile,
            "-out", certfile, "-days", "365", "-subj",
            "/C=US/ST=Test/L=Test/O=HoloBox/CN=localhost"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"  SSL certificates generated successfully!")
        print(f"  Key file: {keyfile}")
        print(f"  Certificate file: {certfile}")
        print("  Note: Browsers will show a security warning for self-signed certificates.")
        
        return keyfile, certfile
        
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not generate SSL certificates: {e}")
        print("Make sure OpenSSL is installed on your system.")
        return None, None
    except FileNotFoundError:
        print("Warning: OpenSSL not found. SSL certificate generation skipped.")
        print("Install OpenSSL to enable automatic HTTPS support.")
        return None, None

# Models
class CameraSettings(BaseModel):
    exposure_us: int | None = None   # microseconds
    gain: float | None = None        # analogue gain

class ExposureMode(BaseModel):
    auto: bool

class ExposureSettings(BaseModel):
    exposure_us: int
    analogue_gain: float

class ResolutionSettings(BaseModel):
    width: int
    height: int

class AWBMode(BaseModel):
    auto: bool

class AWBGains(BaseModel):
    red: float
    blue: float

class ColorMode(BaseModel):
    mode: str  # "rgb", "gray", "r", "g", "b"

class WiFiConfig(BaseModel):
    ssid: str
    password: str | None = None

# Utility functions
def _capture(highRes: bool=False) -> np.ndarray:
    """Capture a frame from the camera"""
    if CAMERA_AVAILABLE:
        if highRes:
            # Store current streaming configuration
            current_res = camera_state["resolution"]
            stream_config = picam.create_video_configuration(main={"size": (current_res["width"], current_res["height"])})
            
            # Switch to high resolution (e.g., 1920x1080 or max available)
            high_res_config = picam.create_video_configuration(main={"size": (1920, 1080)})
            picam.stop()
            picam.configure(high_res_config)
            picam.start()
            
            # Capture high resolution frame
            req = picam.capture_request()
            arr = req.make_array("main")
            req.release()
            
            # Restore streaming configuration immediately
            picam.stop()
            picam.configure(stream_config)
            picam.start()
             
            arr = _crop_image(arr, center=(arr.shape[1] // 2, arr.shape[0] // 2), size=(640, 480))

            return arr
        else:
            # Normal capture at current resolution
            req = picam.capture_request()
            arr = req.make_array("main")
            req.release()
            return arr
    else:
        if highRes:
            print("Mock: High resolution capture requested, using simulated high-res frame.")
            # Create larger mock frame for high resolution
            frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
            cv2.rectangle(frame, (960, 540), (1110, 690), (255, 255, 255), -1)
            frame = _crop_image(frame, center=(frame.shape[1] // 2, frame.shape[0] // 2), size=(640, 480))
            return frame
        else:
            return picam.capture_request().make_array("main")

def _crop_image(img: np.ndarray, center: tuple[int, int], size: tuple[int, int]) -> np.ndarray:
    """Crop image around center to specified size"""
    h, w = img.shape[:2]
    ch, cw = size[1] // 2, size[0] // 2
    x1 = max(0, center[0] - cw)
    y1 = max(0, center[1] - ch)
    x2 = min(w, center[0] + cw)
    y2 = min(h, center[1] + ch)
    return img[y1:y2, x1:x2]

def _restore_stream_config():
    """Restore the streaming configuration after a high-res capture"""
    if CAMERA_AVAILABLE and camera_state["stream_config"] is not None:
        picam.stop()
        picam.configure(camera_state["stream_config"])
        picam.start()

def _jpeg(frame: np.ndarray) -> bytes:
    """Encode frame as JPEG"""
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return buf.tobytes()

# API Endpoints
@app.get("/")
def root():
    """Redirect root URL to the main interface"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html", status_code=301)

@app.get("/favicon.ico")
def favicon():
    "Redirect favicon"
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/assets/favicon.ico", status_code=301)

@app.get("/snapshot", summary="Single JPEG frame")
def snapshot(isHighRes: bool = False) -> Response:
    """Get a single JPEG image from the camera"""
    img = _jpeg(_capture(highRes=isHighRes))
    return Response(content=img, media_type="image/jpeg")

@app.get("/snapshot/highres", summary="High resolution JPEG frame")
def snapshot_highres() -> Response:
    """Get a high resolution JPEG image from the camera"""
    img = _jpeg(_capture(highRes=True))
    return Response(content=img, media_type="image/jpeg")

@app.get("/stream", summary="MJPEG stream")
def stream():
    """Get continuous MJPEG stream"""
    boundary = b"frame"
    def gen():
        camera_state["streaming"] = True
        # Store current stream configuration
        if CAMERA_AVAILABLE:
            camera_state["stream_config"] = picam.create_video_configuration(
                main={"size": (camera_state["resolution"]["width"], camera_state["resolution"]["height"])}
            )
        try:
            while True:
                yield (
                    b"--" + boundary +
                    b"\r\nContent-Type: image/jpeg\r\nCache-Control: no-store\r\n\r\n" +
                    _jpeg(_capture()) + b"\r\n"
                )
                time.sleep(0.05)  # ~20 FPS
        finally:
            camera_state["streaming"] = False
    return StreamingResponse(
        gen(),
        media_type=f"multipart/x-mixed-replace; boundary={boundary.decode()}",
        headers={"Cache-Control": "no-store"}
    )

@app.get("/api/stream.mjpg", summary="MJPEG stream (API endpoint)")
def api_stream():
    """Get continuous MJPEG stream - API endpoint for better compatibility"""
    return stream()

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

@app.post("/api/camera/exposure_mode", summary="Set exposure mode (auto/manual)")
def set_exposure_mode(mode: ExposureMode):
    """Set camera exposure mode"""
    camera_state["exposure_auto"] = mode.auto
    
    if CAMERA_AVAILABLE:
        picam.set_controls({"AeEnable": mode.auto})
    else:
        print(f"Mock: Would set AeEnable to {mode.auto}")
    
    return {"exposure_auto": mode.auto}

@app.post("/api/camera/exposure", summary="Set manual exposure and gain")
def set_exposure_manual(settings: ExposureSettings):
    """Set manual exposure time and analogue gain"""
    if camera_state["exposure_auto"]:
        raise HTTPException(400, "Cannot set manual exposure when auto mode is enabled")
    
    # Validate and clamp values
    exposure_us = max(1, min(1000000, settings.exposure_us))  # 1µs to 1s
    analogue_gain = max(1.0, min(16.0, settings.analogue_gain))  # 1x to 16x
    
    camera_state["exposure_us"] = exposure_us
    camera_state["analogue_gain"] = analogue_gain
    
    if CAMERA_AVAILABLE:
        picam.set_controls({
            "ExposureTime": exposure_us,
            "AnalogueGain": analogue_gain
        })
    else:
        print(f"Mock: Would set ExposureTime={exposure_us}, AnalogueGain={analogue_gain}")
    
    return {
        "exposure_us": exposure_us,
        "analogue_gain": analogue_gain
    }

@app.post("/api/camera/resolution", summary="Set camera resolution")
def set_resolution(resolution: ResolutionSettings):
    """Set camera resolution and restart stream if needed"""
    # Validate resolution
    width = max(64, min(4096, resolution.width))
    height = max(64, min(4096, resolution.height))
    
    camera_state["resolution"] = {"width": width, "height": height}
    
    if CAMERA_AVAILABLE:
        # Stop and reconfigure camera
        picam.stop()
        new_config = picam.create_video_configuration(main={"size": (width, height)})
        picam.configure(new_config)
        picam.start()
    else:
        print(f"Mock: Would reconfigure to {width}x{height}")
    
    return {
        "width": width,
        "height": height,
        "effective_resolution": {"width": width, "height": height}
    }

@app.post("/api/camera/awb_mode", summary="Set white balance mode")
def set_awb_mode(mode: AWBMode):
    """Set white balance mode (auto/manual)"""
    camera_state["awb_auto"] = mode.auto
    
    if CAMERA_AVAILABLE:
        picam.set_controls({"AwbEnable": mode.auto})
    else:
        print(f"Mock: Would set AwbEnable to {mode.auto}")
    
    return {"awb_auto": mode.auto}

@app.post("/api/camera/awb_gains", summary="Set manual white balance gains")
def set_awb_gains(gains: AWBGains):
    """Set manual white balance gains"""
    if camera_state["awb_auto"]:
        raise HTTPException(400, "Cannot set manual white balance when auto mode is enabled")
    
    # Validate and clamp gains
    red_gain = max(0.0, min(8.0, gains.red))
    blue_gain = max(0.0, min(8.0, gains.blue))
    
    camera_state["awb_gains"] = {"red": red_gain, "blue": blue_gain}
    
    if CAMERA_AVAILABLE:
        picam.set_controls({"ColourGains": (red_gain, blue_gain)})
    else:
        print(f"Mock: Would set ColourGains to ({red_gain}, {blue_gain})")
    
    return {
        "red": red_gain,
        "blue": blue_gain
    }

@app.post("/api/camera/color", summary="Set color channel mode")
def set_color_mode(color: ColorMode):
    """Set color channel selection"""
    valid_modes = ["rgb", "gray", "r", "g", "b"]
    if color.mode not in valid_modes:
        raise HTTPException(400, f"Invalid color mode. Must be one of: {valid_modes}")
    
    camera_state["color_mode"] = color.mode
    
    # Note: Color channel processing would be handled in the capture/processing pipeline
    # For now, we just store the preference
    print(f"Color mode set to: {color.mode}")
    
    return {"color_mode": color.mode}

@app.get("/api/camera/status", summary="Get camera status")
def get_camera_status():
    """Get comprehensive camera status"""
    if CAMERA_AVAILABLE:
        try:
            md = picam.capture_metadata()
            # Update state with actual camera values
            camera_state["exposure_us"] = md.get("ExposureTime", camera_state["exposure_us"])
            camera_state["analogue_gain"] = md.get("AnalogueGain", camera_state["analogue_gain"])
        except:
            pass  # Use stored values if metadata unavailable
    
    return {
        "exposure_auto": camera_state["exposure_auto"],
        "exposure_us": camera_state["exposure_us"],
        "analogue_gain": camera_state["analogue_gain"],
        "awb_auto": camera_state["awb_auto"],
        "awb_gains": camera_state["awb_gains"],
        "resolution": camera_state["resolution"],
        "color_mode": camera_state["color_mode"],
        "streaming": camera_state["streaming"]
    }

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
    parser.add_argument("--port", default=80, type=int, help="Port to bind to")
    parser.add_argument("--ssl-keyfile", help="SSL private key file")
    parser.add_argument("--ssl-certfile", help="SSL certificate file")
    parser.add_argument("--no-ssl", action="store_true", default=True, help="Disable automatic SSL certificate generation (default: disabled)")
    args = parser.parse_args()
    
    # Configure SSL
    ssl_kwargs = {}
    
    # If SSL files are explicitly provided, use them
    if args.ssl_keyfile and args.ssl_certfile:
        ssl_kwargs = {
            "ssl_keyfile": args.ssl_keyfile,
            "ssl_certfile": args.ssl_certfile
        }
        print(f"Starting server with SSL on https://{args.host}:{args.port}")
        print(f"Using provided certificates: {args.ssl_keyfile}, {args.ssl_certfile}")
    
    # If no SSL files provided and SSL not disabled, try to auto-generate
    elif not args.no_ssl:
        auto_keyfile, auto_certfile = generate_ssl_certificates_if_needed()
        if auto_keyfile and auto_certfile:
            ssl_kwargs = {
                "ssl_keyfile": auto_keyfile,
                "ssl_certfile": auto_certfile
            }
            print(f"Starting server with auto-generated SSL on https://{args.host}:{args.port}")
        else:
            print(f"Starting server without SSL on http://{args.host}:{args.port}")
            print("SSL certificate generation failed. Running in HTTP mode.")
    
    # SSL explicitly disabled
    else:
        print(f"Starting server without SSL on http://{args.host}:{args.port}")
        print("SSL disabled by --no-ssl flag")
    
    # Show SSL usage information
    if not ssl_kwargs:
        print("For manual SSL support, use --ssl-keyfile and --ssl-certfile arguments")
        print("To disable automatic SSL generation, use --no-ssl")
    
    uvicorn.run(app, host=args.host, port=args.port, **ssl_kwargs)