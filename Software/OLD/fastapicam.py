"""
main.py — FastAPI service for Raspberry Pi cameras (picamera2)
Dependencies:
  pip install fastapi uvicorn numpy opencv-python picamera2
Run:
  uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from picamera2 import Picamera2, StreamConfiguration
import cv2
import numpy as np
import time
import uvicorn

app = FastAPI()
picam = Picamera2()
config = picam.create_video_configuration(main={"size": (640, 480)})
picam.configure(config)
picam.controls.AeEnable = True
picam.start()

# ─── Models ──────────────────────────────────────────────────────────────────────
class CameraSettings(BaseModel):
    exposure_us: int | None = None   # micro-seconds
    gain: float | None = None        # analogue gain

# ─── Utilities ───────────────────────────────────────────────────────────────────
def _jpeg_bytes(frame: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return buf.tobytes()

def _capture() -> np.ndarray:
    # Wait for new frame to minimise duplicates in stream
    picam.wait_for_buffer(frame_id=picam.capture_metadata()["FrameNumber"] + 1)
    return picam.capture_array("main")

# ─── Endpoints ───────────────────────────────────────────────────────────────────
@app.get("/snapshot", summary="Single JPEG frame")
def snapshot() -> Response:
    img = _jpeg_bytes(_capture())
    return Response(content=img, media_type="image/jpeg")

@app.get("/stream", summary="MJPEG stream")
def stream():
    boundary = "frame"
    def gen():
        while True:
            img = _jpeg_bytes(_capture())
            yield (
                b"--" + boundary.encode() + b"\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + img + b"\r\n"
            )
            time.sleep(0.05)  # ≈20 FPS
    headers = {"Content-Type": f"multipart/x-mixed-replace; boundary={boundary}"}
    return StreamingResponse(gen(), media_type=headers["Content-Type"])

@app.post("/settings", summary="Set exposure and/or gain")
def set_settings(s: CameraSettings):
    controls = {}
    if s.exposure_us is not None:
        controls["ExposureTime"] = int(s.exposure_us)
        picam.controls.AeEnable = False
    if s.gain is not None:
        controls["AnalogueGain"] = float(s.gain)
    if not controls:
        raise HTTPException(400, "No parameters supplied")
    picam.set_controls(controls)
    return {"applied": controls}

@app.get("/settings", summary="Current exposure/gain")
def get_settings():
    md = picam.capture_metadata()
    return {
        "exposure_us": md.get("ExposureTime", None),
        "gain": md.get("AnalogueGain", None),
        "auto_exposure": bool(picam.controls.AeEnable),
    }

@app.get("/stats", summary="Min/Max/Mean pixel values of a fresh frame")
def stats():
    img = _capture()
    # Convert to grayscale for luminance stats
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return {
        "min": int(np.min(gray)),
        "max": int(np.max(gray)),
        "mean": float(np.mean(gray)),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
