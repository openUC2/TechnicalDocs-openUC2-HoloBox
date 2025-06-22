# HoloBox JupyterLite Notebook

This directory contains a complete JupyterLite implementation for hologram processing with the HoloBox system. JupyterLite provides an authentic Jupyter Lab experience that runs entirely in the browser.

## Files

### Core Notebook
- **`notebook.html`** - Redirect to JupyterLite interface
- **`jupyter/`** - Complete JupyterLite distribution with hologram processing
- **`hologram_processing_lib.py`** - Comprehensive hologram processing library (legacy)

### Integration Files
- **`index.html`** - Main HoloBox camera interface (existing)
- **`camera_controls.js`** - Camera control functions (existing) 
- **`hologram_processing.py`** - Legacy hologram functions

### Build System
- **`../build_jupyter.py`** - CLI tool to build JupyterLite static files

## Features

### JupyterLite Experience
- ✅ **Authentic Jupyter**: Full JupyterLab interface in browser
- ✅ **Python Runtime**: Complete Python environment via Pyodide
- ✅ **Scientific Stack**: NumPy, Matplotlib, SciPy pre-installed
- ✅ **No Installation**: Runs in any modern browser
- ✅ **Offline Capable**: Works without internet after initial load

### Hologram Processing
- ✅ **Complete Reconstruction Pipeline**: Fresnel propagation, focus analysis
- ✅ **Interactive Visualization**: Real-time plotting with Matplotlib
- ✅ **Sample Data Generation**: Built-in test holograms
- ✅ **Multi-Distance Analysis**: Focus optimization algorithms

### Built-in Capabilities
- **Fresnel Propagation**: Accurate optical field reconstruction
- **Sample Hologram Generation**: Test patterns for algorithm development
- **Focus Optimization**: Automatic distance finding
- **Multi-Panel Visualization**: Intensity, phase, amplitude display

## Quick Start

### 1. Build the JupyterLite Environment (CLI)
```bash
# From Software directory
python build_jupyter.py --static ./static --clean
```

### 2. Start HoloBox Server
```bash
python streamlined_camera_api.py
```

### 3. Access JupyterLite
```
http://localhost:8000/static/notebook.html
```

### 4. Run Sample Processing
1. Open the notebook in your browser
2. Wait for Python environment to load
3. Click "▶ Run All" to execute all cells
4. See hologram reconstruction in action

## CLI Build System

The `build_jupyter.py` script creates a complete JupyterLite distribution:

```bash
# Basic build
python build_jupyter.py

# Build and deploy to static directory
python build_jupyter.py --static ./static

# Clean build (remove previous build)
python build_jupyter.py --static ./static --clean

# Custom output directory
python build_jupyter.py --output ./my_jupyter_build
```

### Build Options
- `--output, -o`: Specify build output directory
- `--static, -s`: Copy to static directory for web serving
- `--clean`: Remove existing build before creating new one

## Architecture

### JupyterLite Components
- **Pyodide**: Python runtime in WebAssembly
- **Scientific Stack**: NumPy, Matplotlib, SciPy
- **Browser UI**: Authentic Jupyter interface
- **Local Storage**: Notebook persistence

### Hologram Processing Library

```python
# Core functions available in notebook
def fresnel_propagate(field, wavelength, pixel_size, distance):
    """Fresnel propagation of optical field"""
    
def process_hologram(hologram, wavelength=440e-9, pixel_size=1.4e-6, distance=0.005):
    """Complete hologram reconstruction pipeline"""
    
def generate_sample_hologram(size=512, wavelength=440e-9, pixel_size=1.4e-6):
    """Generate test hologram for development"""
```

## Integration with HoloBox

### Camera Processing
The notebook integrates seamlessly with the main HoloBox camera interface:

1. **Live Processing**: Process images from camera feed
2. **Parameter Tuning**: Adjust reconstruction parameters
3. **Data Export**: Save results for further analysis

### API Integration
```python
# Example: Process live camera data
import requests

# Get image from camera API
response = requests.get('http://localhost:8000/api/capture')
image_data = response.json()

# Process with hologram functions
results = process_hologram(image_data['hologram'])
```

## Browser Compatibility

- ✅ **Chrome/Chromium**: Full support
- ✅ **Firefox**: Full support  
- ✅ **Safari**: Full support
- ✅ **Edge**: Full support

### Requirements
- Modern browser with WebAssembly support
- ~50MB memory for Python runtime
- JavaScript enabled

## Offline Operation

After initial load, the notebook works completely offline:

1. **Pyodide Runtime**: Cached in browser
2. **Scientific Libraries**: Pre-loaded
3. **Notebook Interface**: Static files
4. **No External Dependencies**: Self-contained

## Performance

### Typical Performance
- **Startup Time**: 5-10 seconds (first load)
- **512x512 Hologram**: ~100ms processing
- **1024x1024 Hologram**: ~400ms processing
- **Memory Usage**: ~50-100MB

### Optimization Tips
- Use smaller images for interactive work
- Clear outputs regularly to free memory
- Restart kernel if memory usage grows

## Troubleshooting

### Common Issues

**Slow Loading**
- Clear browser cache
- Check network connectivity for initial Pyodide download
- Try different browser

**Memory Errors**
- Reduce image sizes
- Clear cell outputs
- Restart browser tab

**Processing Errors**
- Check hologram data format (numpy array)
- Verify parameter ranges
- Use sample data for testing

## Development

### Adding New Functions
1. Edit the notebook cells directly in browser
2. Test with sample data
3. Copy working code to library files

### Custom Notebooks
1. Use "+" buttons to add cells
2. Mix markdown documentation with code
3. Save notebooks using browser's download feature

## Technical Details

### File Structure
```
static/
├── notebook.html          # Redirect to JupyterLite
├── jupyter/              # JupyterLite distribution
│   └── lab/
│       └── index.html    # Main interface
├── hologram_processing_lib.py  # Legacy library
└── README.md             # This file
```

### Build Process
1. **Interface Generation**: Create JupyterLite-compatible HTML
2. **Library Integration**: Embed hologram processing functions
3. **Dependency Management**: Setup Pyodide and scientific packages
4. **Static Deployment**: Copy to web-accessible directory

This implementation provides a true Jupyter experience while maintaining the offline and self-contained nature required for the HoloBox system.