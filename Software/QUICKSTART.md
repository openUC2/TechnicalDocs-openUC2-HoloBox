# HoloBox Offline Jupyter Notebook - Quick Start Guide

## 🚀 Getting Started

### 1. Start the HoloBox Server
```bash
cd Software
python streamlined_camera_api.py --port 8000
```

### 2. Access the Offline Notebook
Open your browser and navigate to:
```
http://localhost:8000/static/notebook.html
```

### 3. Initialize the Notebook
1. Click **"Run All Cells"** button at the top
2. Wait for all cells to execute (you'll see ✅ checkmarks)
3. Click **"Generate Sample Hologram"** to create test data
4. Click **"Process Hologram"** to see reconstruction

## 🎯 Core Features

### Interactive Parameters
- **Wavelength**: 400-700 nm (blue to red light)
- **Pixel Size**: 0.5-5.0 µm (camera sensor specifications)  
- **Distance**: 0.1-20.0 mm (reconstruction focal distance)

### Visualization Panels
- **Original Hologram**: Raw input data
- **Reconstructed Image**: Focused reconstruction
- **Phase Information**: Phase component visualization
- **Amplitude Information**: Amplitude component visualization

### Cell Types
1. **Introduction**: Overview of capabilities
2. **Imports & Setup**: Initialize processing library
3. **Core Functions**: Load hologram algorithms
4. **Demo Functions**: Interactive demonstration setup
5. **Interactive Parameters**: Real-time controls
6. **Results Display**: Multi-panel visualization
7. **Integration Info**: Connection to main system

## 🔬 Usage Workflows

### Basic Hologram Processing
1. Run all cells to initialize
2. Generate or load a hologram
3. Adjust parameters using sliders
4. Process to see real-time reconstruction
5. Analyze different components (intensity, phase, amplitude)

### Parameter Optimization
1. Start with default parameters
2. Adjust wavelength to match your light source
3. Set pixel size to match your camera
4. Use distance slider to find optimal focus
5. Observe intensity changes in real-time

### Advanced Analysis
- Use the comprehensive library for custom processing
- Access raw data through browser developer console
- Export parameters for use in main system
- Compare multiple reconstruction distances

## 🔧 Technical Details

### Browser Requirements
- **Chrome/Edge**: Full support ✅
- **Firefox**: Full support ✅  
- **Safari**: Limited PyScript support ⚠️

### Performance Tips
- Use 256×256 images for real-time processing
- Larger images (512×512+) may be slower
- Enable hardware acceleration in browser settings
- Close other browser tabs for better performance

### Offline Operation
- All dependencies are bundled locally
- Graceful fallback to CDN if local files fail
- No internet required once page is loaded
- Works in airgapped/isolated environments

## 🌐 Integration with Main System

### Live Camera Processing
The notebook can be extended to work with live camera feeds from the main HoloBox interface.

### Parameter Synchronization  
Parameters optimized in the notebook can be transferred to the main camera system for live processing.

### API Integration
See `hologram_integration_example.py` for examples of:
- Live frame processing endpoints
- Auto-focus functionality
- Parameter synchronization
- Hologram streaming

## 📊 Example Data

### Sample Holograms
The notebook includes built-in sample hologram generation:
- **Circles**: Multiple circular objects with interference
- **Lines**: Linear interference patterns
- **Random**: Random structured patterns

### Real Data
To use real hologram data:
1. Replace the sample generation with your data loading
2. Ensure data is normalized to [0,1] range
3. Convert to grayscale if needed
4. Process using the same reconstruction pipeline

## 🛠️ Customization

### Adding New Algorithms
Edit `hologram_processing_lib.py`:
```python
class HologramProcessor:
    def my_new_algorithm(self, hologram, parameters):
        # Your custom processing
        return result
```

### Custom Visualization
Add new canvas elements to the HTML and corresponding display functions in the PyScript code.

### Parameter Ranges
Modify slider ranges in the HTML to match your specific requirements.

## 🔍 Troubleshooting

### Common Issues

**PyScript not loading:**
- Check browser console for errors
- Verify internet connection for CDN fallback
- Try refreshing the page

**Canvas not displaying:**
- Ensure arrays are properly normalized [0,1]
- Check browser support for ImageData API
- Verify canvas dimensions match array size

**Slow performance:**
- Reduce image size (use 128×128 or 256×256)
- Close other browser tabs
- Check CPU usage in browser task manager

**Parameter updates not working:**
- Verify slider event handlers are connected
- Check browser console for JavaScript errors
- Ensure cells are executed in order

### Browser Console
Open developer tools (F12) to see:
- Python execution logs
- Error messages
- Performance information
- Raw data access

## 📚 Additional Resources

- **Main Documentation**: `/static/README.md`
- **API Reference**: See `hologram_processing_lib.py` docstrings
- **Integration Examples**: `hologram_integration_example.py`
- **Test Suite**: `test_offline_notebook.py`

## 🤝 Support

For issues or questions:
1. Check the test suite results
2. Review browser console for errors  
3. Verify all files are properly served
4. Check the comprehensive documentation

## 🎉 Next Steps

Once familiar with the offline notebook:
1. Try integrating with live camera data
2. Experiment with different hologram types
3. Optimize parameters for your specific setup
4. Extend the library with custom algorithms
5. Share parameters with the main HoloBox system

The offline notebook provides a complete development and analysis environment for hologram processing, seamlessly integrated with the HoloBox ecosystem!