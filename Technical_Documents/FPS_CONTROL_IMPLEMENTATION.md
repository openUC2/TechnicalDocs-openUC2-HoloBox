# Processing FPS Control Implementation

## Summary
Added UI control for hologram processing frame rate (FPS) with 1 FPS default as requested.

## Changes Made

### 1. Frontend UI (index.html)

#### Added FPS Slider Control
- **Location**: Hologram Processing Parameters panel
- **Range**: 0.5 to 5 FPS
- **Default**: 1 FPS (1000ms interval)
- **Features**: 
  - +/- buttons for fine adjustment
  - Real-time value display
  - Helpful tooltip: "Lower FPS = less CPU usage, smoother camera stream"

#### JavaScript Functions Added
- **`window.adjustSlider(sliderId, delta)`**: Global function to adjust any slider value with +/- buttons
- **`initializeSliders()`**: Initializes all slider event listeners including:
  - `processingFps`: Updates processing interval in Python
  - `dz`: Distance parameter
  - `wavelength`: Wavelength parameter
  - `pixelsize`: Pixel size parameter

### 2. Backend Processing (hologram_processing.py)

#### New Global Variable
```python
current_interval_ms = 1000  # Default to 1 FPS (1000ms)
```

#### New Function: `update_processing_interval(interval_ms)`
- **Purpose**: Dynamically update processing interval from JavaScript
- **Behavior**:
  - Updates global `current_interval_ms` variable
  - If processing is active: restarts timer with new interval
  - If processing is stopped: stores setting for next activation
  - Logs changes to console with FPS calculation

#### Modified Function: `toggle_processing()`
- Now uses `current_interval_ms` instead of hardcoded 1000ms
- Displays current FPS in status message
- Logs FPS when starting/stopping

#### JavaScript Interface
- Exported `window.update_processing_interval` function
- Can be called from browser console or UI controls
- Seamlessly integrates with PyScript/Pyodide environment

### 3. Other Improvements

#### Debug Mode Default Changed
```python
debug_mode = False  # Disabled by default (was True)
```
This reduces console spam as requested.

## Usage

### User Interface
1. Open "Hologram Processing Parameters" panel
2. Adjust "Processing Rate" slider (0.5 - 5 FPS)
3. Use +/- buttons for precise control
4. Value updates immediately when processing is enabled

### Programmatic Control
```javascript
// Set processing to 2 FPS (500ms interval)
window.update_processing_interval(500);

// Set processing to 0.5 FPS (2000ms interval)
window.update_processing_interval(2000);
```

## Performance Impact

### FPS Settings Guide
- **0.5 FPS** (2000ms): Minimal CPU usage, best for long-term monitoring
- **1 FPS** (1000ms): **Default** - balanced performance and responsiveness
- **2 FPS** (500ms): More responsive, moderate CPU usage
- **5 FPS** (200ms): High responsiveness, highest CPU usage

### Camera Stream Performance
Lower processing FPS = smoother camera stream due to:
- Less main thread blocking from `getImageData()`
- More time for MJPEG stream rendering
- Reduced memory allocation/deallocation

## Technical Notes

### Interval Restart Mechanism
When processing is active and interval is changed:
1. Current `setInterval` is cleared with `clearInterval()`
2. New `setInterval` created with updated interval
3. Timer proxy is reused (no recreation needed)
4. No processing frames are lost during transition

### FPS Calculation
```
FPS = 1000 / interval_ms
interval_ms = 1000 / FPS
```

### Integration with PyScript
- Uses `create_proxy()` for JavaScript interop
- Properly manages memory with proxy lifecycle
- Updates are immediate with no page reload needed

## Testing

### Verify Installation
1. Open browser console
2. Check for: `✅ Global functions exported: processStaticImage, update_processing_interval`
3. Test: `window.update_processing_interval(500)` should log interval change

### Verify UI Control
1. Enable hologram processing
2. Adjust FPS slider
3. Check console for: `⚙️ Processing interval updated to Xms (Y FPS)`
4. Observe status message updates

## Related Files
- `/Software/static/index.html` - UI and JavaScript
- `/Software/static/hologram_processing.py` - Python processing logic
- `/Technical_Documents/HOLOGRAM_PROCESSING_FIX.md` - Previous optimizations
- `/Technical_Documents/STREAMING_OPTIMIZATION.md` - Backend streaming fixes

## Next Steps (Optional)

### Consider Web Worker Implementation
Current implementation still blocks main thread during `getImageData()`. Future enhancement:
- Move image processing to Web Worker
- Use `OffscreenCanvas` for non-blocking image capture
- Send results back to main thread for display

This would completely eliminate processing impact on camera stream.
