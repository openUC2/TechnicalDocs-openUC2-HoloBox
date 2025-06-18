# Digital Hologram Processing - Educational Jupyter Notebook

## Overview

This Jupyter notebook provides an interactive educational experience for understanding digital holography using the OpenUC2 HoloBox system. It combines theoretical explanations with practical implementation, allowing students and researchers to explore holographic imaging concepts hands-on.

## Features

- **📚 Comprehensive Theory**: Step-by-step explanation of holographic imaging physics
- **🧮 Interactive Mathematics**: Live implementation of Fresnel propagation algorithms
- **🎛️ Parameter Controls**: Interactive sliders to explore parameter effects
- **📷 Live Camera Integration**: Real-time processing with HoloBox camera API
- **🧪 Hands-on Exercises**: Guided experiments to deepen understanding
- **🎯 Optimization Guide**: Best practices for high-quality results

## Installation

### Prerequisites

- Python 3.7 or higher
- Jupyter Notebook or JupyterLab

### Install Dependencies

```bash
# Navigate to the Software directory
cd Software

# Install notebook dependencies
pip install -r notebook_requirements.txt

# Enable jupyter widgets (if needed)
jupyter nbextension enable --py widgetsnbextension
```

### For JupyterLab Users

```bash
# Install JupyterLab widget extension
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

## Usage

### 1. Starting the Notebook

```bash
# Start Jupyter Notebook
jupyter notebook hologram_education_notebook.ipynb

# OR start JupyterLab
jupyter lab hologram_education_notebook.ipynb
```

### 2. Camera Integration (Optional)

To use the live camera features, you need to run the HoloBox camera server:

```bash
# In a separate terminal, start the camera API server
python streamlined_camera_api.py --host 0.0.0.0 --port 8000
```

The notebook will connect to `http://localhost:8000` by default. You can change this in the notebook's configuration cell.

### 3. Working Through the Notebook

The notebook is structured as a progressive learning experience:

1. **Theory Introduction** - Understanding holography basics
2. **Setup** - Importing libraries and configuring connections
3. **Mathematical Implementation** - Core Fresnel propagation algorithms
4. **Synthetic Demonstrations** - Learning with simulated data
5. **Interactive Exploration** - Parameter effects with live controls
6. **Live Camera Integration** - Real-time hologram processing
7. **Advanced Analysis** - Diffraction regimes and optimization
8. **Exercises** - Hands-on learning activities

## Educational Content

### Learning Objectives

After completing this notebook, students will understand:

- Physical principles of holographic imaging
- Mathematical foundations of wave propagation
- Fresnel diffraction and its applications
- Digital signal processing techniques for holography
- Parameter optimization for best results
- Practical considerations for experimental setup

### Key Concepts Covered

- **Wave Optics**: Interference, diffraction, and propagation
- **Fourier Optics**: FFT-based wave field manipulation
- **Digital Signal Processing**: Sampling, aliasing, and frequency domain
- **Image Processing**: Reconstruction algorithms and optimization
- **Experimental Design**: Parameter selection and measurement strategies

## API Integration

The notebook connects to the HoloBox camera API for live image processing:

### Supported Endpoints

- `GET /snapshot` - Capture single frame
- `GET /stream` - MJPEG video stream
- `POST /settings` - Set camera parameters (exposure, gain)
- `GET /stats` - Image statistics

### Camera Parameters

- **Exposure Time**: Controls light sensitivity (microseconds)
- **Analogue Gain**: Amplification factor
- **Focus**: Should be slightly defocused for hologram recording

## Troubleshooting

### Common Issues

1. **Dependencies not installed**
   ```bash
   pip install --upgrade jupyter ipywidgets matplotlib numpy
   ```

2. **Widgets not displaying**
   ```bash
   jupyter nbextension enable --py widgetsnbextension --sys-prefix
   ```

3. **Camera connection failed**
   - Check that the camera server is running
   - Verify the API URL in the notebook configuration
   - Ensure no firewall is blocking the connection

4. **Performance issues**
   - Use smaller crop sizes for faster processing
   - Close other applications to free memory
   - Consider using a more powerful computer for real-time processing

### Performance Optimization

- **Crop Size**: Use power-of-2 sizes (256, 512) for efficient FFT
- **Parameter Updates**: Avoid very frequent slider updates
- **Memory Management**: Restart kernel if memory usage becomes high

## Educational Applications

### Suitable for:

- **Undergraduate Physics Courses**: Optics and wave phenomena
- **Graduate Research**: Advanced holographic techniques
- **Engineering Programs**: Optical system design
- **Self-directed Learning**: Independent exploration of holography

### Prerequisites:

- Basic understanding of wave physics
- Python programming knowledge
- Familiarity with NumPy and Matplotlib

## Hardware Requirements

### Minimum:
- CPU: Dual-core processor
- RAM: 4GB
- Storage: 1GB free space

### Recommended:
- CPU: Quad-core processor
- RAM: 8GB or more
- Storage: 2GB free space
- GPU: Optional, for accelerated computing

## Further Resources

### Related Projects
- [OpenUC2 Main Repository](https://github.com/openUC2/UC2-GIT)
- [HoloBox Hardware Designs](../Production_Files/)
- [Assembly Guides](../Technical_Documents/)

### Academic References
- Digital holography textbooks and papers
- Fourier optics literature
- Computer vision and image processing resources

## Contributing

We welcome contributions to improve this educational resource:

1. **Bug Reports**: Open issues for any problems encountered
2. **Feature Requests**: Suggest new educational content or features
3. **Content Improvements**: Enhance explanations or add examples
4. **Code Optimization**: Improve performance or readability

## License

This educational notebook is part of the OpenUC2 project and follows the same open-source licensing terms.

---

**Happy Learning!** 🔬✨

*This notebook demonstrates how theory and practice can be combined for effective learning in optical sciences and engineering.*