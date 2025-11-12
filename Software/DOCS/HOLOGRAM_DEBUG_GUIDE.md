# HoloBox Debug and Testing Guide

## Overview
This guide explains how to test and debug the hologram processing system on your computer without relying on PyScript for both **Inline Holography** (`index.html`) and **Off-Axis Holography** (`index_offaxis.html`).

## What was implemented

### 1. Debug Controls (Both Pages)
- Added a new "🔧 Debug & Testing Controls" panel to both `index.html` and `index_offaxis.html`
- Force JavaScript Fallback Mode toggle
- OpenCV.js integration toggle  
- Test current processing mode button
- Real-time processing mode status indicator

### 2. Fallback System Improvements
- Fixed `HologramProcessorOpenCV` vs `HologramProcessorFallback` naming issue
- Added automatic OpenCV.js loading for off-axis pages when in fallback mode
- Created `OffAxisHologramProcessor` class for simplified off-axis reconstruction
- Enhanced inline holography fallback support
- Improved error handling and initialization

### 3. Forced Fallback Mode
- Set `isIOS = 1;` in `pyscript_fallback_loader.js` to force fallback mode for debugging
- Automatic OpenCV.js loading when fallback is used
- Supports both inline and off-axis holographic processing

## How to Test

### Method 1: Using the Debug Controls (Recommended)

#### For Inline Holography (`index.html`):
1. Open `index.html` in your browser
2. Look for the "🔧 Debug & Testing Controls" panel (may be collapsed)
3. Check "Force JavaScript Fallback Mode"
4. Check "Enable OpenCV.js for Enhanced Processing" for better processing
5. Click "Test Current Mode" to verify everything works
6. Use the normal hologram controls to test inline processing

#### For Off-Axis Holography (`index_offaxis.html`):
1. Open `index_offaxis.html` in your browser
2. Look for the "🔧 Debug & Testing Controls" panel (may be collapsed)
3. Check "Force JavaScript Fallback Mode"
4. Check "Enable OpenCV.js for Full Processing" for complete reconstruction
5. Click "Test Current Mode" to verify everything works
6. Use the ROI selection and off-axis controls to test processing

### Method 2: Automatic Mode (Current Setup)
Since `isIOS = 1;` is set in the code:
1. Open either `index.html` or `index_offaxis.html` in your browser
2. The system will automatically use JavaScript fallback mode
3. OpenCV.js will be loaded automatically when needed
4. Check the console for initialization messages

## What to Look For

### Console Messages
- `🚀 Starting PyScript/Fallback initialization...`
- `🔀 Using fallback mode based on platform detection`
- `📥 Loading OpenCV.js for off-axis processing...` (off-axis)
- `🚀 Initializing general/inline fallback processor` (inline)
- `🚀 Initializing off-axis fallback processor` (off-axis)
- `✅ OpenCV.js runtime initialized`
- `✅ JavaScript fallback initialized successfully`

### Visual Indicators
- Processing mode status in the debug panel
- Color-coded alerts:
  - 🟢 Green = Full processing with OpenCV.js
  - 🟡 Yellow = Limited processing (forced mode)
  - 🔵 Blue = Fallback mode (auto-detected)
  - ⚪ Gray = Loading/Unknown
- Fallback notification at the top of the page

### Functionality

#### Inline Holography:
- Camera stream should work normally
- Basic hologram processing with intensity patterns
- Enhanced processing with OpenCV.js if enabled

#### Off-Axis Holography:
- Camera stream should work normally
- ROI selection on the Fourier transform canvas
- Four panels: Live feed, FFT, Amplitude, Phase
- Real-time or manual processing

## Troubleshooting

### Issue: "HologramProcessorOpenCV is not defined"
- **Solution**: This was fixed by improving the script loading order
- The fallback loader now properly waits for all scripts to load
- Check that `js/hologram_processing_fallback.js` exists

### Issue: OpenCV.js not loading
- **Check**: Browser console for network errors
- **Solution**: The system falls back to simplified processing without OpenCV.js
- **Alternative**: Manually enable via debug controls
- **Network**: Requires internet connection for OpenCV.js CDN

### Issue: Processing not working
- **Check**: Processing mode status in debug panel
- **Test**: Click "Test Current Mode" button
- **Debug**: Look for JavaScript errors in console
- **Verify**: Camera stream is working first

### Issue: Different behavior between inline and off-axis
- **Expected**: Off-axis requires more complex processing
- **Inline**: Simpler intensity-based processing
- **Off-axis**: FFT-based reconstruction with ROI selection

## File Changes Made

1. **index.html** (NEW):
   - Added debug controls panel
   - Enhanced JavaScript initialization
   - Better fallback integration for inline holography

2. **index_offaxis.html**:
   - Added debug controls panel
   - Enhanced JavaScript initialization  
   - Better fallback integration for off-axis holography

3. **pyscript_fallback_loader.js**:
   - Fixed class name resolution
   - Added automatic OpenCV.js loading
   - Improved error handling
   - Set `isIOS = 1` for forced debugging
   - Enhanced support for both inline and off-axis pages

4. **hologram_processing_fallback.js**:
   - Added `OffAxisHologramProcessor` class
   - Enhanced `HologramProcessorOpenCV` for inline processing
   - Simplified reconstruction algorithms
   - Better event listener management

## Development Notes

### For Normal Operation:
Change `isIOS = 1;` back to `isIOS = this.isIOSDevice();` in `pyscript_fallback_loader.js`

### For Extended Testing:
- Use the debug controls to switch between modes
- Monitor console output for detailed logging
- Test with and without OpenCV.js
- Compare inline vs off-axis behavior

### Performance Notes:
- JavaScript fallback is slower than PyScript+NumPy
- OpenCV.js provides better FFT processing but requires more memory
- Inline holography is generally faster than off-axis
- Simplified mode works without external dependencies

## Page-Specific Features

### Inline Holography (`index.html`):
- ✅ Basic intensity-based hologram processing
- ✅ Real-time camera stream processing
- ✅ JavaScript + OpenCV.js fallback
- ✅ Debug controls integration

### Off-Axis Holography (`index_offaxis.html`):
- ✅ FFT-based holographic reconstruction
- ✅ ROI selection for cross-correlation term
- ✅ Four-panel display (Live, FFT, Amplitude, Phase)
- ✅ Advanced processing parameters
- ✅ JavaScript + OpenCV.js fallback
- ✅ Debug controls integration