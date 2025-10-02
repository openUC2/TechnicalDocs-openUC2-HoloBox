# HoloBox Camera API - Enhanced GUI Features

## 🆕 New High-Resolution Snap Feature

This enhancement adds a new "Snap High-Res" functionality to the HoloBox camera interface.

### Features Added:

#### 1. **High-Resolution Capture Button**
- **Location**: Next to Start/Stop Stream buttons in Camera Controls
- **Button**: 📸 Snap High-Res (Orange/Warning style)
- **Functionality**: 
  - Stops the current stream
  - Captures a high-resolution image (1920x1080)
  - Displays the static image in the same `<img>` tag as the stream
  - Processes the static high-res image instead of the stream

#### 2. **Backend API Enhancements**
- **New Endpoint**: `/snapshot/highres` - Dedicated high-resolution capture
- **Enhanced Function**: `_capture(highRes=True)` with proper camera configuration management
- **Stream State Management**: Maintains low-resolution streaming settings when resuming

#### 3. **Smart Mode Switching**
- **Snap Mode**: When activated, stream is stopped and high-res image is displayed
- **Resume Stream**: Button changes to "🔄 Resume Stream" to restart streaming
- **State Preservation**: Stream settings (resolution, exposure, etc.) are maintained

#### 4. **Static Image Processing**
- **PyScript Integration**: `window.processStaticImage()` function for processing static images
- **Same Processing Pipeline**: Uses identical hologram processing on static high-res images
- **Boundary Box Support**: ROI selection works on both stream and static images

### Usage:

1. **Start with Stream**: Click "Start Stream" for live video feed
2. **Capture High-Res**: Click "📸 Snap High-Res" to stop stream and capture static high-resolution image
3. **Process Static**: The hologram processing automatically switches to process the static image
4. **Resume Stream**: Click "🔄 Resume Stream" to return to live streaming mode

### Technical Details:

#### Backend Changes:
```python
# Enhanced _capture function with proper config management
def _capture(highRes: bool=False) -> np.ndarray:
    if highRes:
        # Store current streaming config
        # Switch to high-res (1920x1080)  
        # Capture frame
        # Restore streaming config
```

#### Frontend Changes:
```javascript
// New snap functionality
const snapHighRes = () => {
    // Stop stream, capture high-res, display static image
    // Toggle between snap mode and stream mode
    // Manage UI state and processing pipeline
}
```

#### Processing Integration:
```python
# PyScript static image processing
window.processStaticImage = create_proxy(lambda: process_image_for_hologram())
```

### Benefits:

1. **Higher Quality Processing**: High-resolution captures provide better detail for hologram processing
2. **Flexible Workflow**: Users can choose between live streaming or high-quality static processing
3. **Preserved Settings**: All camera settings are maintained when switching between modes  
4. **Seamless Integration**: Same processing pipeline works for both stream and static images
5. **User-Friendly**: Clear visual indicators and intuitive button behavior

### API Endpoints:

- `GET /snapshot/highres` - Capture high-resolution image
- `GET /snapshot?isHighRes=true` - Alternative high-res capture method
- `GET /api/camera/status` - Check camera state including streaming status

### Files Modified:

- `streamlined_camera_api.py` - Backend API enhancements
- `static/index.html` - Added snap button and styling
- `static/camera_controls.js` - Snap functionality and mode management  
- `static/hologram_processing.py` - Static image processing support

This enhancement maintains backward compatibility while adding powerful new functionality for high-quality hologram processing.