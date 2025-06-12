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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)