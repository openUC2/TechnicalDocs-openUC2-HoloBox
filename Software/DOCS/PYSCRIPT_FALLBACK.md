# PyScript iOS/iPad Fallback System

## Overview

This fallback system provides compatibility for iOS and iPadOS devices where PyScript/Pyodide may not work reliably due to platform limitations.

## Problem

PyScript and Pyodide rely on WebAssembly and, in some cases, `SharedArrayBuffer` for full functionality. iOS/iPadOS (Safari and Chrome) have known limitations:

- Limited `SharedArrayBuffer` support
- WebAssembly memory restrictions
- Worker thread limitations
- General instability with Pyodide on iOS

This affects iPad users, who represent a significant portion of the educational and scientific community.

## Solution

An automatic fallback system that:

1. **Detects iOS/iPad devices** at page load
2. **Checks for PyScript initialization** with a timeout
3. **Automatically switches** to pure JavaScript implementation if PyScript fails
4. **Notifies users** about the fallback mode and its limitations
5. **Provides 1:1 API compatibility** between Python and JavaScript implementations

## Files

### Core Files

- **`js/pyscript_fallback_loader.js`** - Main detection and switching logic
  - Detects iOS/iPad devices
  - Checks WebAssembly and SharedArrayBuffer support
  - Monitors PyScript initialization with timeout
  - Loads fallback implementation when needed

- **`js/hologram_processing_fallback.js`** - JavaScript fallback implementation
  - Pure JavaScript version of hologram processing functions
  - Simplified processing without full FFT
  - Compatible API with Python version

### Modified Files

- **`index.html`** - Main hologram processing page (added fallback loader)
- **`index_offaxis.html`** - Off-axis holography page (added fallback loader)

## How It Works

### Detection Process

1. **Platform Detection**
   ```javascript
   - Check user agent for iPad/iPhone/iPod
   - Check for iPad Pro (MacIntel + touch points)
   - Verify WebAssembly support
   - Check SharedArrayBuffer availability
   ```

2. **PyScript Monitoring**
   ```javascript
   - Wait up to 10 seconds for PyScript initialization
   - Check for pyscript/pyodide global objects
   - Monitor py-script element attributes
   ```

3. **Automatic Fallback**
   ```javascript
   - Load JavaScript fallback implementation
   - Initialize event listeners
   - Show user notification
   - Update UI indicators
   ```

### User Experience

When fallback mode is active:

- **Visual Notification**: A prominent banner appears explaining the fallback mode
- **Status Indicators**: UI shows "Fallback Mode" in status areas
- **Functionality Note**: Users are informed about processing limitations
- **Graceful Degradation**: Basic functionality works without full holographic reconstruction

## Limitations in Fallback Mode

### Standard Hologram Processing (`index.html`)

✅ **Available:**
- Camera stream viewing
- Image capture
- Basic image transformations (flip, rotate)
- ROI selection and visualization
- Parameter adjustment
- Basic intensity display

⚠️ **Limited:**
- Full Fourier Transform processing
- Complete Fresnel propagation
- Advanced holographic reconstruction

### Off-Axis Holography (`index_offaxis.html`)

❌ **Not Available:**
- Off-axis holographic reconstruction requires extensive FFT operations
- Digital refocusing
- Phase retrieval
- Complete frequency domain processing

**Note**: For full off-axis processing, use a desktop computer or Android device.

## API Compatibility

The JavaScript fallback implements the same functions as the Python version:

### Python API
```python
def process_image_for_hologram():
    # Full processing with NumPy and FFT
    ...

def toggle_processing(event):
    # Start/stop processing
    ...

def update_parameters(event):
    # Update wavelength, pixel size, etc.
    ...
```

### JavaScript API
```javascript
processImageForHologram() {
    // Simplified processing
    ...
}

toggleProcessing(event) {
    // Start/stop processing
    ...
}

updateParameters(event) {
    // Update wavelength, pixel size, etc.
    ...
}
```

## Testing

### Desktop Testing

Test the fallback by forcing fallback mode:

```javascript
// In browser console
window.pyScriptFallbackLoader.initializeFallback();
```

### iOS/iPad Testing

Simply open the page on an iPad or iPhone:
- Safari: Full detection should work
- Chrome on iOS: Also properly detected
- iPad Pro: Detected via MacIntel + touch points

### Monitoring Detection

Check the console for detection logs:

```
🔍 Initializing PyScript Fallback Loader...
📊 Platform Detection:
  - iOS/iPadOS: true/false
  - WebAssembly: true/false
  - SharedArrayBuffer: true/false
⚠️ iOS/iPadOS detected - PyScript/Pyodide may not work reliably
🔄 Initializing JavaScript fallback...
✅ JavaScript fallback initialized successfully
```

## Configuration

### Timeout Adjustment

Change PyScript initialization timeout in `pyscript_fallback_loader.js`:

```javascript
this.pyScriptTimeout = 10000; // milliseconds
```

### Force Fallback Mode

To always use fallback (for testing):

```javascript
// In pyscript_fallback_loader.js, shouldUseFallback()
shouldUseFallback() {
    return true; // Force fallback
}
```

### Disable Fallback Notification

```javascript
// In pyscript_fallback_loader.js, initializeFallback()
// Comment out this line:
// this.showFallbackNotification();
```

## Future Enhancements

Potential improvements:

1. **Full FFT in JavaScript**: Integrate a JavaScript FFT library (e.g., fft.js) for complete processing
2. **WebGL Acceleration**: Use WebGL for faster image processing
3. **Progressive Enhancement**: Detect available features and enable accordingly
4. **Feature Detection API**: Expose a clear API to check available features
5. **Graceful Mode Switching**: Allow runtime switching between modes

## Troubleshooting

### Fallback Not Activating

- Check browser console for errors
- Verify `pyscript_fallback_loader.js` is loaded
- Check if PyScript is actually failing or just slow

### UI Elements Not Working

- Ensure element IDs match between Python and JavaScript versions
- Check console for JavaScript errors
- Verify event listeners are attached

### Processing Not Working

- Verify camera stream is active
- Check that image data is being captured
- Look for errors in browser console

## Contributing

When adding new processing features:

1. Implement in Python first (`hologram_processing.py`)
2. Create JavaScript equivalent in `hologram_processing_fallback.js`
3. Ensure API compatibility (same function names, parameters)
4. Update this documentation
5. Test on both desktop and iOS devices

## Support

For issues specific to iOS/iPad compatibility, please include:

- Device model and iOS version
- Browser and version
- Console errors
- Whether fallback mode activated correctly

## References

- [PyScript Documentation](https://pyscript.net/)
- [Pyodide Documentation](https://pyodide.org/)
- [iOS WebAssembly Limitations](https://webkit.org/blog/7734/webassembly-on-ios/)
- [SharedArrayBuffer and iOS](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
