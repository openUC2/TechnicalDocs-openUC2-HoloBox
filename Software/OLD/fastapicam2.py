# fastapicam.py  (rev-2, for picamera2 ≥ 0.3)
#
# run:  uvicorn fastapicam:app --host 0.0.0.0 --port 8000
#
# uses capture_request API (replaces old wait_for_buffer)  :contentReference[oaicite:0]{index=0}

from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from picamera2 import Picamera2
import numpy as np
import cv2
import time
import uvicorn

app = FastAPI()

picam = Picamera2()
picam.configure(picam.create_video_configuration(main={"size": (640, 480)}))
picam.start()


class CameraSettings(BaseModel):
    exposure_us: int | None = None
    gain: float | None = None


def _capture():
    req = picam.capture_request()              # blocks until fresh frame
    arr = req.make_array("main")
    req.release()
    return arr


def _jpeg(frame: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return buf.tobytes()


@app.get("/snapshot")
def snapshot():
    return Response(_jpeg(_capture()), media_type="image/jpeg")


@app.get("/stream")
def stream():
    boundary = b"frame"
    def gen():
        while True:
            yield (
                b"--" + boundary +
                b"\r\nContent-Type: image/jpeg\r\n\r\n" +
                _jpeg(_capture()) + b"\r\n"
            )
            time.sleep(0.05)                   # ~20 FPS
    return StreamingResponse(
        gen(),
        media_type=f"multipart/x-mixed-replace; boundary={boundary.decode()}",
    )


@app.post("/settings")
def set_settings(s: CameraSettings):
    controls = {}
    if s.exposure_us is not None:
        controls["ExposureTime"] = int(s.exposure_us)
    if s.gain is not None:
        controls["AnalogueGain"] = float(s.gain)
    if not controls:
        raise HTTPException(400, "no parameters supplied")
    picam.set_controls(controls)
    return controls


@app.get("/settings")
def get_settings():
    md = picam.capture_metadata()
    return {
        "exposure_us": md.get("ExposureTime"),
        "gain": md.get("AnalogueGain"),
    }


@app.get("/stats")
def stats():
    gray = cv2.cvtColor(_capture(), cv2.COLOR_BGR2GRAY)
    return {
        "min": int(np.min(gray)),
        "max": int(np.max(gray)),
        "mean": float(np.mean(gray)),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
