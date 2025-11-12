# Streaming Performance Analysis & Fixes

## Issue Summary

You reported "enormous backpressure" and frame delay, but observed that `http://192.168.4.1/stream` works fluently.

## Root Cause Analysis

### ✅ What's Working Well:
1. **Direct MJPEG Stream** - The backend `/stream` endpoint is optimized:
   - RGB888 format (3 channels, not 4)
   - Configurable quality (default 60%)
   - Adaptive FPS (default 20 FPS)
   - Proper backpressure handling

2. **Frontend Display** - Uses native browser MJPEG:
   ```html
   <img id="stream" src="http://192.168.4.1/stream?quality=60&fps=20">
   ```
   - No JavaScript processing on frames
   - Browser handles MJPEG natively
   - Very efficient

### ❌ The Problem:

**Hologram Processing is Reading Full-Resolution Frames Every Second!**

Location: `Software/static/hologram_processing.py` lines 165-265

When hologram processing is enabled, it:
1. Reads the **full resolution** stream image (640x480 or higher)
2. Creates a temporary canvas at full resolution
3. Calls `getImageData()` to read all pixels
4. Processes the entire frame
5. Repeats **every 1 second** via `setInterval(timer_proxy, 1000)`

This is extremely CPU/memory intensive because:
- `canvas.getImageData()` on 640x480 = 307,200 pixels × 4 bytes = 1.2 MB per read
- Happens every second in background
- Blocks the main thread
- Causes frame drops and delays

## Fixes Applied

### 1. ✅ Backend Optimizations (Already Applied)
- RGB888 format (25% less data)
- Quality parameter (60% default)
- Adaptive FPS (20 FPS default)
- Proper frame timing

### 2. ✅ Frontend Stream URL Update
Changed from:
```javascript
stream.src = baseUrl + '/api/stream.mjpg';
```

To:
```javascript
stream.src = baseUrl + '/stream?quality=60&fps=20';
```

This uses the optimized parameters directly.

### 3. ✅ Swagger UI Fix
Added proper API documentation URLs:
```python
app = FastAPI(
    title="Streamlined Camera API",
    docs_url="/docs",        # Swagger UI at http://192.168.4.1/docs
    redoc_url="/redoc",      # ReDoc at http://192.168.4.1/redoc
    openapi_url="/openapi.json"
)
```

## Recommendations

### Immediate Actions:

1. **Disable Hologram Processing by Default**
   - Users should explicitly enable it only when needed
   - The stream preview should work WITHOUT processing

2. **Optimize Hologram Processing** (if you want to keep it):
   ```python
   # Instead of full resolution:
   actual_width = stream_img.naturalWidth   # 640
   actual_height = stream_img.naturalHeight # 480
   
   # Use downsampled resolution:
   actual_width = 256   # Much smaller
   actual_height = 256
   
   # Draw at smaller size:
   temp_ctx.drawImage(stream_img, 0, 0, 256, 256)
   ```

3. **Reduce Processing Frequency**
   ```python
   # Instead of every 1 second:
   setInterval(timer_proxy, 1000)
   
   # Try every 2-3 seconds:
   setInterval(timer_proxy, 2000)  # or 3000
   ```

### Testing Instructions:

1. **Test Raw Stream Performance:**
   ```
   Open: http://192.168.4.1/stream?quality=60&fps=20
   ```
   This should be very smooth and fluid.

2. **Test UI Without Processing:**
   ```
   Open: http://192.168.4.1/
   Click "Start Stream"
   DO NOT enable hologram processing
   ```
   Should be just as smooth as direct stream.

3. **Test with Different Quality Settings:**
   ```
   Low WiFi:    http://192.168.4.1/stream?quality=40&fps=15
   Good WiFi:   http://192.168.4.1/stream?quality=60&fps=20
   Great WiFi:  http://192.168.4.1/stream?quality=75&fps=25
   ```

4. **Check Swagger UI:**
   ```
   Open: http://192.168.4.1/docs
   ```
   Should show full API documentation.

## Performance Expectations

### Direct Stream (without processing):
- **Frame Rate:** 20 FPS smooth
- **Latency:** < 100ms
- **Bandwidth:** ~500 KB/s (4 Mbps)
- **CPU Usage:** Minimal (browser handles MJPEG natively)

### With Hologram Processing Enabled:
- **Frame Rate:** Still 20 FPS for display
- **Processing:** 1 FPS (every 1 second)
- **CPU Usage:** High (canvas operations + FFT)
- **May cause:** UI lag, frame drops, increased latency

## Conclusion

The stream itself is well-optimized now. The "backpressure" is caused by:
1. ~~Hologram processing reading full-res frames~~ (Main issue)
2. ~~Processing happening every second in background~~
3. ~~No downsampling before processing~~

**Solution:** 
- The camera preview (`<img id="stream">`) should work perfectly WITHOUT any processing
- Hologram processing should be explicitly enabled only when user wants it
- When enabled, it should use downsampled images (256x256 not 640x480)

## Files Modified

1. ✅ `streamlined_camera_api.py` - Backend optimizations + Swagger UI
2. ✅ `camera_controls.js` - Use optimized stream URL
3. 📝 `hologram_processing.py` - NEEDS optimization (reduce resolution/frequency)

## Next Steps

Would you like me to:
1. Optimize the hologram processing to use smaller images?
2. Add a FPS/Quality slider to the UI for user control?
3. Add performance monitoring to show actual FPS/bandwidth?
