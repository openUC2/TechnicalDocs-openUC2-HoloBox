# HoloBox Offline Jupyter Notebook

This directory contains a self-contained, offline-capable Jupyter-like notebook implementation for hologram processing with the HoloBox system.

## Files

### Core Notebook
- **`notebook.html`** - Main notebook interface with Jupyter-like cells, runs entirely in browser
- **`hologram_processing_lib.py`** - Comprehensive hologram processing library
- **`vendor/`** - Offline dependencies for internet-free operation

### Integration Files
- **`index.html`** - Main HoloBox camera interface (existing)
- **`camera_controls.js`** - Camera control functions (existing) 
- **`hologram_processing.py`** - PyScript hologram functions (existing)

## Features

### Offline Operation
- ✅ **No Internet Required**: All dependencies bundled locally
- ✅ **Fallback to CDN**: Graceful degradation if local files fail
- ✅ **Self-Contained**: Works in isolated/airgapped environments

### Jupyter-Like Interface
- ✅ **Multiple Cell Types**: Markdown and code cells
- ✅ **Interactive Execution**: Run individual cells or all at once
- ✅ **Rich Output**: Text, images, and interactive controls
- ✅ **Persistent State**: Variables maintained between cell executions

### Hologram Processing
- ✅ **Fresnel Propagation**: Digital refocusing using Fresnel kernels
- ✅ **Real-time Parameters**: Interactive wavelength, pixel size, distance controls
- ✅ **Visualization**: Original, reconstructed, phase, and amplitude displays
- ✅ **Sample Generation**: Built-in test hologram generation
- ✅ **Auto-focus**: Automatic optimal distance finding

### Integration Ready
- ✅ **FastAPI Compatible**: Served via existing static file system
- ✅ **Camera Integration**: Ready for live hologram processing
- ✅ **Modular Design**: Library can be used in other contexts

## Usage

### Quick Start
1. **Open Notebook**: Navigate to `http://localhost:8000/static/notebook.html`
2. **Run All Cells**: Click "Run All Cells" button
3. **Generate Sample**: Click "Generate Sample Hologram"
4. **Process**: Click "Process Hologram" to see reconstruction
5. **Adjust Parameters**: Use sliders to change wavelength, pixel size, distance

### Interactive Parameters
- **Wavelength**: 400-700 nm (default: 440nm blue)
- **Pixel Size**: 0.5-5.0 µm (default: 1.4µm typical camera)
- **Distance**: 0.1-20.0 mm (default: 5.0mm reconstruction distance)

### Cell Structure
1. **Introduction** - Overview and features
2. **Imports & Setup** - Initialize libraries and hologram processor
3. **Core Functions** - Load hologram processing library
4. **Demo Functions** - Set up demonstration and visualization
5. **Interactive Parameters** - Real-time parameter controls
6. **Results Display** - Multi-panel visualization (original, reconstructed, phase, amplitude)
7. **Integration Info** - How to use with main HoloBox system

## Library API

### HologramProcessor Class
```python
from hologram_processing_lib import HologramProcessor

# Initialize processor
processor = HologramProcessor(wavelength=440e-9, pixel_size=1.4e-6)

# Process hologram
results = processor.reconstruct_hologram(hologram, distance=0.005)
# Returns: {'intensity', 'complex_field', 'phase', 'amplitude'}

# Auto-focus
focus_info = processor.find_optimal_distance(hologram, (0.001, 0.010))
# Returns: {'optimal_distance', 'distances', 'focus_scores'}

# Generate test data
test_hologram = processor.create_sample_hologram(256, 'circles')
```

### Convenience Functions
```python
# Simple processing
result = process_hologram_simple(hologram, distance=0.005)

# Create demo data
demo_hologram = create_demo_hologram(size=256)

# Find best focus
focus_result = find_focus(hologram, min_dist=0.001, max_dist=0.010)
```

## Integration with Main System

### Live Camera Processing
The notebook can be extended to process live camera feeds:

```python
# In main camera system
from static.hologram_processing_lib import HologramProcessor

processor = HologramProcessor()

# Process live frame
camera_frame = get_camera_frame()
results = processor.reconstruct_hologram(camera_frame, current_distance)
return results['intensity']  # Send reconstructed image to client
```

### Parameter Synchronization
Parameters from the notebook can be synchronized with the main interface:
- Wavelength settings
- Pixel size calibration  
- Focus distance optimization

## Technical Details

### PyScript Integration
- Uses PyScript 2025.5.1 for Python in browser
- NumPy and Matplotlib support for scientific computing
- Direct canvas rendering for fast image display

### Offline Dependencies
- **Bootstrap 5.3.3**: UI framework (local fallback)
- **PyScript Core**: Python runtime (local fallback)
- **Hologram Library**: Comprehensive processing functions

### Performance
- Optimized Fresnel propagation using NumPy FFT
- Real-time parameter updates
- Efficient canvas rendering for visualization
- Batch processing support for multiple distances

## Troubleshooting

### Common Issues
1. **PyScript Loading**: Check browser console for errors
2. **Canvas Display**: Ensure arrays are properly normalized
3. **Parameter Updates**: Verify slider event handlers are connected

### Browser Compatibility
- **Chrome/Edge**: Full support
- **Firefox**: Full support  
- **Safari**: Limited PyScript support

### Performance Tips
- Use smaller hologram sizes (256x256) for faster processing
- Process multiple distances in batch for efficiency
- Enable browser GPU acceleration if available

## Future Enhancements

### Planned Features
- [ ] **Export Functionality**: Save results as images/data
- [ ] **Advanced Filters**: Noise reduction, enhancement filters
- [ ] **3D Reconstruction**: Volume rendering from z-stack
- [ ] **Machine Learning**: AI-powered focus optimization
- [ ] **Real-time Streaming**: Live hologram processing

### Integration Opportunities
- [ ] **Database Storage**: Save processing parameters and results
- [ ] **Remote Processing**: Offload computation to server
- [ ] **Collaborative**: Multiple users sharing notebook state
- [ ] **Mobile**: Touch-optimized interface for tablets

## Contributing

### Development Setup
1. Modify `hologram_processing_lib.py` for new algorithms
2. Update `notebook.html` for interface changes
3. Test offline functionality by disconnecting internet
4. Ensure fallback mechanisms work properly

### Adding New Algorithms
```python
# In hologram_processing_lib.py
class HologramProcessor:
    def new_algorithm(self, hologram, parameters):
        """Your new processing algorithm"""
        # Implementation here
        return result
```

## License

Same license as the main HoloBox project.