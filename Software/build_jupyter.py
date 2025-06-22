#!/usr/bin/env python3
"""
CLI tool to build JupyterLite static files for HoloBox offline notebook.

This script downloads and configures JupyterLite with hologram processing
capabilities for offline use.
"""

import os
import sys
import json
import shutil
import urllib.request
import zipfile
import tempfile
import argparse
from pathlib import Path

# JupyterLite version to use
JUPYTERLITE_VERSION = "0.4.7"
JUPYTERLITE_DOWNLOAD_URL = f"https://github.com/jupyterlite/jupyterlite/releases/download/v{JUPYTERLITE_VERSION}/jupyterlite-{JUPYTERLITE_VERSION}.tgz"

class JupyterLiteBuilder:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.temp_dir = None
        
    def create_config(self):
        """Create JupyterLite configuration for offline operation."""
        config = {
            "LiteBuildConfig": {
                "federated_extensions": [],
                "ignore_sys_prefix": [],
                "pip": [],
                "output_dir": str(self.output_dir),
                "contents": ["notebooks"],
                "pyodide_url": "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js",
                "piplite_urls": ["https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"]
            }
        }
        
        config_path = self.output_dir / "jupyter_lite_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config_path
        
    def create_notebooks_dir(self):
        """Create notebooks directory with hologram processing example."""
        notebooks_dir = self.output_dir / "notebooks"
        notebooks_dir.mkdir(exist_ok=True)
        
        # Create a sample hologram processing notebook
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# HoloBox Hologram Processing\n",
                        "\n",
                        "This notebook provides hologram processing capabilities for the HoloBox system.\n",
                        "It runs entirely in your browser without requiring a Python installation.\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import numpy as np\n",
                        "import matplotlib.pyplot as plt\n",
                        "from scipy import ndimage\n",
                        "import io\n",
                        "import base64\n",
                        "\n",
                        "print('HoloBox Hologram Processing Library Loaded!')\n",
                        "print('Available functions:')\n",
                        "print('- process_hologram(hologram, wavelength, pixel_size, distance)')\n",
                        "print('- generate_sample_hologram(size, wavelength, pixel_size)')\n",
                        "print('- find_focus(hologram, wavelength, pixel_size, distance_range)')"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "def fresnel_propagate(field, wavelength, pixel_size, distance):\n",
                        "    \"\"\"\n",
                        "    Fresnel propagation of optical field.\n",
                        "    \n",
                        "    Parameters:\n",
                        "    field: 2D complex array - input optical field\n",
                        "    wavelength: float - wavelength in meters\n",
                        "    pixel_size: float - pixel size in meters\n",
                        "    distance: float - propagation distance in meters\n",
                        "    \n",
                        "    Returns:\n",
                        "    2D complex array - propagated field\n",
                        "    \"\"\"\n",
                        "    ny, nx = field.shape\n",
                        "    \n",
                        "    # Frequency coordinates\n",
                        "    fx = np.fft.fftfreq(nx, pixel_size)\n",
                        "    fy = np.fft.fftfreq(ny, pixel_size)\n",
                        "    FX, FY = np.meshgrid(fx, fy)\n",
                        "    \n",
                        "    # Wave number\n",
                        "    k = 2 * np.pi / wavelength\n",
                        "    \n",
                        "    # Fresnel transfer function\n",
                        "    H = np.exp(1j * np.pi * wavelength * distance * (FX**2 + FY**2))\n",
                        "    \n",
                        "    # Propagate\n",
                        "    field_fft = np.fft.fft2(field)\n",
                        "    propagated_fft = field_fft * H\n",
                        "    propagated_field = np.fft.ifft2(propagated_fft)\n",
                        "    \n",
                        "    return propagated_field"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "def process_hologram(hologram, wavelength=440e-9, pixel_size=1.4e-6, distance=0.005):\n",
                        "    \"\"\"\n",
                        "    Process hologram and reconstruct the object field.\n",
                        "    \n",
                        "    Parameters:\n",
                        "    hologram: 2D array - input hologram intensity\n",
                        "    wavelength: float - wavelength in meters (default: 440nm)\n",
                        "    pixel_size: float - pixel size in meters (default: 1.4µm)\n",
                        "    distance: float - reconstruction distance in meters (default: 5mm)\n",
                        "    \n",
                        "    Returns:\n",
                        "    dict with reconstruction results\n",
                        "    \"\"\"\n",
                        "    # Convert hologram to complex field (assume plane wave reference)\n",
                        "    hologram_normalized = hologram / np.max(hologram)\n",
                        "    field = np.sqrt(hologram_normalized).astype(complex)\n",
                        "    \n",
                        "    # Propagate to reconstruction plane\n",
                        "    reconstructed = fresnel_propagate(field, wavelength, pixel_size, distance)\n",
                        "    \n",
                        "    # Calculate intensity, phase, and amplitude\n",
                        "    intensity = np.abs(reconstructed)**2\n",
                        "    phase = np.angle(reconstructed)\n",
                        "    amplitude = np.abs(reconstructed)\n",
                        "    \n",
                        "    return {\n",
                        "        'intensity': intensity,\n",
                        "        'phase': phase,\n",
                        "        'amplitude': amplitude,\n",
                        "        'complex_field': reconstructed\n",
                        "    }"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "def generate_sample_hologram(size=512, wavelength=440e-9, pixel_size=1.4e-6):\n",
                        "    \"\"\"\n",
                        "    Generate a sample hologram for testing.\n",
                        "    \n",
                        "    Parameters:\n",
                        "    size: int - image size (size x size)\n",
                        "    wavelength: float - wavelength in meters\n",
                        "    pixel_size: float - pixel size in meters\n",
                        "    \n",
                        "    Returns:\n",
                        "    2D array - sample hologram\n",
                        "    \"\"\"\n",
                        "    # Create coordinate arrays\n",
                        "    x = np.arange(size) * pixel_size\n",
                        "    y = np.arange(size) * pixel_size\n",
                        "    X, Y = np.meshgrid(x - x.mean(), y - y.mean())\n",
                        "    \n",
                        "    # Create object (multiple point sources)\n",
                        "    object_field = np.zeros((size, size), dtype=complex)\n",
                        "    \n",
                        "    # Add some point sources at different positions\n",
                        "    positions = [(-100e-6, -50e-6), (80e-6, 30e-6), (0, 100e-6)]\n",
                        "    distances = [3e-3, 4e-3, 5e-3]  # Different distances for each point\n",
                        "    \n",
                        "    for (px, py), dist in zip(positions, distances):\n",
                        "        # Create spherical wave from point source\n",
                        "        r = np.sqrt((X - px)**2 + (Y - py)**2 + dist**2)\n",
                        "        k = 2 * np.pi / wavelength\n",
                        "        point_wave = np.exp(1j * k * r) / r\n",
                        "        object_field += point_wave\n",
                        "    \n",
                        "    # Reference wave (plane wave)\n",
                        "    reference = np.ones((size, size), dtype=complex)\n",
                        "    \n",
                        "    # Hologram is interference pattern\n",
                        "    total_field = object_field + reference\n",
                        "    hologram = np.abs(total_field)**2\n",
                        "    \n",
                        "    # Add some noise\n",
                        "    noise = np.random.normal(0, 0.01 * np.max(hologram), hologram.shape)\n",
                        "    hologram += noise\n",
                        "    \n",
                        "    return np.maximum(hologram, 0)  # Ensure non-negative"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Generate and display a sample hologram\n",
                        "sample_hologram = generate_sample_hologram(512)\n",
                        "\n",
                        "plt.figure(figsize=(12, 4))\n",
                        "\n",
                        "plt.subplot(1, 3, 1)\n",
                        "plt.imshow(sample_hologram, cmap='gray')\n",
                        "plt.title('Sample Hologram')\n",
                        "plt.colorbar()\n",
                        "\n",
                        "# Process the hologram\n",
                        "results = process_hologram(sample_hologram, distance=0.004)\n",
                        "\n",
                        "plt.subplot(1, 3, 2)\n",
                        "plt.imshow(results['intensity'], cmap='hot')\n",
                        "plt.title('Reconstructed Intensity')\n",
                        "plt.colorbar()\n",
                        "\n",
                        "plt.subplot(1, 3, 3)\n",
                        "plt.imshow(results['phase'], cmap='hsv')\n",
                        "plt.title('Reconstructed Phase')\n",
                        "plt.colorbar()\n",
                        "\n",
                        "plt.tight_layout()\n",
                        "plt.show()\n",
                        "\n",
                        "print(f'Hologram shape: {sample_hologram.shape}')\n",
                        "print(f'Intensity range: {results[\"intensity\"].min():.2e} - {results[\"intensity\"].max():.2e}')\n",
                        "print(f'Phase range: {results[\"phase\"].min():.2f} - {results[\"phase\"].max():.2f}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Interactive Parameter Testing\n",
                        "\n",
                        "Try different reconstruction distances to see how the focus changes:"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Test different reconstruction distances\n",
                        "distances = [0.002, 0.003, 0.004, 0.005, 0.006]\n",
                        "\n",
                        "plt.figure(figsize=(15, 3))\n",
                        "\n",
                        "for i, dist in enumerate(distances):\n",
                        "    result = process_hologram(sample_hologram, distance=dist)\n",
                        "    \n",
                        "    plt.subplot(1, len(distances), i+1)\n",
                        "    plt.imshow(result['intensity'], cmap='hot')\n",
                        "    plt.title(f'Distance: {dist*1000:.1f}mm')\n",
                        "    plt.axis('off')\n",
                        "\n",
                        "plt.tight_layout()\n",
                        "plt.show()\n",
                        "\n",
                        "print('Reconstruction at different distances shows how focus varies with propagation distance.')"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.11.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        notebook_path = notebooks_dir / "hologram_processing.ipynb"
        with open(notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=2)
            
        return notebook_path
        
    def create_jupyterlite_html(self):
        """Create a JupyterLite-compatible HTML interface."""
        print("Creating JupyterLite-compatible interface...")
        
        # Create output directory structure
        output_dir = self.output_dir / "_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create lab directory
        lab_dir = output_dir / "lab"
        lab_dir.mkdir(exist_ok=True)
        
        # Create the main index.html for JupyterLite
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoloBox JupyterLite</title>
    <link rel="icon" type="image/x-icon" href="https://jupyter.org/favicon.ico">
    
    <!-- Pyodide CSS -->
    <style>
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: #fff;
        }
        
        .header {
            background: #2e7d32;
            color: white;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .logo {
            display: flex;
            align-items: center;
            font-size: 18px;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        .notebook-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .cell {
            border: 1px solid #e0e0e0;
            margin: 10px 0;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .cell-toolbar {
            background: #f5f5f5;
            padding: 5px 10px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 12px;
            color: #666;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .cell-content {
            position: relative;
        }
        
        .code-cell .cell-content {
            background: #f8f8f8;
        }
        
        .markdown-cell .cell-content {
            background: white;
            padding: 15px;
        }
        
        .code-input {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: #f8f8f8;
            border: none;
            width: 100%;
            padding: 10px;
            resize: vertical;
            min-height: 100px;
            font-size: 13px;
            line-height: 1.4;
        }
        
        .code-output {
            border-top: 1px solid #e0e0e0;
            padding: 10px;
            background: white;
            white-space: pre-wrap;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
        }
        
        .run-button {
            background: #1976d2;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 11px;
        }
        
        .run-button:hover {
            background: #1565c0;
        }
        
        .run-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .toolbar {
            background: #f5f5f5;
            padding: 10px 20px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .toolbar button {
            background: #1976d2;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .toolbar button:hover {
            background: #1565c0;
        }
        
        .status {
            margin-left: auto;
            font-size: 12px;
            color: #666;
        }
        
        .error {
            color: #d32f2f;
            background: #ffebee;
            padding: 10px;
            border-left: 4px solid #d32f2f;
            margin: 5px 0;
        }
        
        .success {
            color: #388e3c;
            background: #e8f5e8;
            padding: 10px;
            border-left: 4px solid #388e3c;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            🔬 HoloBox JupyterLite
        </div>
        <div>
            <span id="python-status">Loading Python...</span>
        </div>
    </div>
    
    <div class="toolbar">
        <button onclick="runAllCells()">▶ Run All</button>
        <button onclick="clearAllOutputs()">🗑 Clear Outputs</button>
        <button onclick="addCell('code')">+ Code</button>
        <button onclick="addCell('markdown')">+ Markdown</button>
        <div class="status">
            <span id="execution-status">Ready</span>
        </div>
    </div>
    
    <div id="loading" class="loading">
        <h3>Loading Python Environment...</h3>
        <p>Please wait while we initialize the scientific computing environment.</p>
    </div>
    
    <div id="notebook-container" class="notebook-container" style="display: none;">
        <!-- Cells will be added here -->
    </div>

    <!-- Pyodide -->
    <script src="https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js"></script>
    
    <script>
        let pyodide;
        let cellCounter = 0;
        
        // Initialize Pyodide
        async function initPyodide() {
            try {
                pyodide = await loadPyodide();
                
                // Install required packages
                document.getElementById('python-status').textContent = 'Installing packages...';
                await pyodide.loadPackage(["numpy", "matplotlib", "scipy"]);
                
                // Setup matplotlib for web
                await pyodide.runPython(`
                    import matplotlib
                    matplotlib.use('Agg')
                    import matplotlib.pyplot as plt
                    import numpy as np
                    from scipy import ndimage
                    import io
                    import base64
                    
                    def show_plot():
                        """Convert current matplotlib figure to base64 for display"""
                        import io
                        import base64
                        
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                        buf.seek(0)
                        img_b64 = base64.b64encode(buf.getvalue()).decode()
                        buf.close()
                        plt.close()  # Close the figure to free memory
                        
                        return f'<img src="data:image/png;base64,{img_b64}" style="max-width: 100%; height: auto;">'
                `);
                
                document.getElementById('python-status').textContent = 'Python Ready';
                document.getElementById('loading').style.display = 'none';
                document.getElementById('notebook-container').style.display = 'block';
                
                // Load default notebook
                loadDefaultNotebook();
                
            } catch (error) {
                console.error('Failed to initialize Pyodide:', error);
                document.getElementById('loading').innerHTML = 
                    '<h3>Failed to Load Python</h3><p>Error: ' + error.message + '</p>';
            }
        }
        
        function createCell(cellType, content = '', isExecuted = false) {
            cellCounter++;
            const cellId = `cell-${cellCounter}`;
            
            const cellDiv = document.createElement('div');
            cellDiv.className = `cell ${cellType}-cell`;
            cellDiv.id = cellId;
            
            if (cellType === 'code') {
                cellDiv.innerHTML = `
                    <div class="cell-toolbar">
                        <span>Code [${cellCounter}]</span>
                        <button class="run-button" onclick="runCell('${cellId}')">Run</button>
                    </div>
                    <div class="cell-content">
                        <textarea class="code-input" placeholder="Enter Python code...">${content}</textarea>
                        <div class="code-output" style="display: none;"></div>
                    </div>
                `;
            } else {
                cellDiv.innerHTML = `
                    <div class="cell-toolbar">
                        <span>Markdown [${cellCounter}]</span>
                        <button class="run-button" onclick="renderMarkdown('${cellId}')">Render</button>
                    </div>
                    <div class="cell-content">
                        <textarea class="code-input" placeholder="Enter Markdown...">${content}</textarea>
                    </div>
                `;
            }
            
            return cellDiv;
        }
        
        function addCell(cellType) {
            const container = document.getElementById('notebook-container');
            const cell = createCell(cellType);
            container.appendChild(cell);
        }
        
        async function runCell(cellId) {
            const cell = document.getElementById(cellId);
            const input = cell.querySelector('.code-input');
            const output = cell.querySelector('.code-output');
            const runButton = cell.querySelector('.run-button');
            
            if (!pyodide) {
                alert('Python environment not ready');
                return;
            }
            
            const code = input.value;
            if (!code.trim()) return;
            
            runButton.disabled = true;
            runButton.textContent = 'Running...';
            document.getElementById('execution-status').textContent = 'Executing...';
            
            try {
                // Capture matplotlib plots
                const result = await pyodide.runPython(`
import sys
from io import StringIO
import traceback

# Capture stdout
old_stdout = sys.stdout
sys.stdout = mystdout = StringIO()

# Capture any plots
plots_html = ""

try:
    exec("""${code.replace(/"/g, '\\"')}""")
    
    # Check if there's a current figure
    import matplotlib.pyplot as plt
    if plt.get_fignums():
        plots_html = show_plot()
    
    stdout_value = mystdout.getvalue()
    sys.stdout = old_stdout
    
    # Combine text output and plots
    output_html = ""
    if stdout_value:
        output_html += f"<pre>{stdout_value}</pre>"
    if plots_html:
        output_html += plots_html
    
    output_html if output_html else "Executed successfully"
    
except Exception as e:
    sys.stdout = old_stdout
    f"Error: {str(e)}\\n{traceback.format_exc()}"
                `);
                
                output.innerHTML = result;
                output.style.display = 'block';
                
            } catch (error) {
                output.innerHTML = `<div class="error">Error: ${error.message}</div>`;
                output.style.display = 'block';
            }
            
            runButton.disabled = false;
            runButton.textContent = 'Run';
            document.getElementById('execution-status').textContent = 'Ready';
        }
        
        async function runAllCells() {
            const cells = document.querySelectorAll('.code-cell');
            for (let cell of cells) {
                await runCell(cell.id);
                // Small delay between cells
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
        
        function clearAllOutputs() {
            const outputs = document.querySelectorAll('.code-output');
            outputs.forEach(output => {
                output.innerHTML = '';
                output.style.display = 'none';
            });
        }
        
        function renderMarkdown(cellId) {
            const cell = document.getElementById(cellId);
            const input = cell.querySelector('.code-input');
            const content = cell.querySelector('.cell-content');
            
            // Simple markdown rendering (just headers and paragraphs)
            let markdown = input.value;
            markdown = markdown.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            markdown = markdown.replace(/^## (.*$)/gim, '<h2>$1</h2>');
            markdown = markdown.replace(/^# (.*$)/gim, '<h1>$1</h1>');
            markdown = markdown.replace(/\\n/g, '<br>');
            
            content.innerHTML = `
                <div style="padding: 15px;">
                    ${markdown}
                </div>
            `;
        }
        
        function loadDefaultNotebook() {
            const container = document.getElementById('notebook-container');
            
            // Add title markdown cell
            const titleCell = createCell('markdown', `# HoloBox Hologram Processing

This notebook provides hologram processing capabilities for the HoloBox system.
It runs entirely in your browser without requiring a Python installation.`);
            container.appendChild(titleCell);
            
            // Add import cell
            const importCell = createCell('code', `import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import io
import base64

print('HoloBox Hologram Processing Library Loaded!')
print('Available functions:')
print('- process_hologram(hologram, wavelength, pixel_size, distance)')
print('- generate_sample_hologram(size, wavelength, pixel_size)')
print('- find_focus(hologram, wavelength, pixel_size, distance_range)')`);
            container.appendChild(importCell);
            
            // Add processing functions
            const functionsCell = createCell('code', `def fresnel_propagate(field, wavelength, pixel_size, distance):
    """
    Fresnel propagation of optical field.
    
    Parameters:
    field: 2D complex array - input optical field
    wavelength: float - wavelength in meters
    pixel_size: float - pixel size in meters
    distance: float - propagation distance in meters
    
    Returns:
    2D complex array - propagated field
    """
    ny, nx = field.shape
    
    # Frequency coordinates
    fx = np.fft.fftfreq(nx, pixel_size)
    fy = np.fft.fftfreq(ny, pixel_size)
    FX, FY = np.meshgrid(fx, fy)
    
    # Wave number
    k = 2 * np.pi / wavelength
    
    # Fresnel transfer function
    H = np.exp(1j * np.pi * wavelength * distance * (FX**2 + FY**2))
    
    # Propagate
    field_fft = np.fft.fft2(field)
    propagated_fft = field_fft * H
    propagated_field = np.fft.ifft2(propagated_fft)
    
    return propagated_field

def process_hologram(hologram, wavelength=440e-9, pixel_size=1.4e-6, distance=0.005):
    """
    Process hologram and reconstruct the object field.
    
    Parameters:
    hologram: 2D array - input hologram intensity
    wavelength: float - wavelength in meters (default: 440nm)
    pixel_size: float - pixel size in meters (default: 1.4µm)
    distance: float - reconstruction distance in meters (default: 5mm)
    
    Returns:
    dict with reconstruction results
    """
    # Convert hologram to complex field (assume plane wave reference)
    hologram_normalized = hologram / np.max(hologram)
    field = np.sqrt(hologram_normalized).astype(complex)
    
    # Propagate to reconstruction plane
    reconstructed = fresnel_propagate(field, wavelength, pixel_size, distance)
    
    # Calculate intensity, phase, and amplitude
    intensity = np.abs(reconstructed)**2
    phase = np.angle(reconstructed)
    amplitude = np.abs(reconstructed)
    
    return {
        'intensity': intensity,
        'phase': phase,
        'amplitude': amplitude,
        'complex_field': reconstructed
    }

def generate_sample_hologram(size=512, wavelength=440e-9, pixel_size=1.4e-6):
    """
    Generate a sample hologram for testing.
    
    Parameters:
    size: int - image size (size x size)
    wavelength: float - wavelength in meters
    pixel_size: float - pixel size in meters
    
    Returns:
    2D array - sample hologram
    """
    # Create coordinate arrays
    x = np.arange(size) * pixel_size
    y = np.arange(size) * pixel_size
    X, Y = np.meshgrid(x - x.mean(), y - y.mean())
    
    # Create object (multiple point sources)
    object_field = np.zeros((size, size), dtype=complex)
    
    # Add some point sources at different positions
    positions = [(-100e-6, -50e-6), (80e-6, 30e-6), (0, 100e-6)]
    distances = [3e-3, 4e-3, 5e-3]  # Different distances for each point
    
    for (px, py), dist in zip(positions, distances):
        # Create spherical wave from point source
        r = np.sqrt((X - px)**2 + (Y - py)**2 + dist**2)
        k = 2 * np.pi / wavelength
        point_wave = np.exp(1j * k * r) / r
        object_field += point_wave
    
    # Reference wave (plane wave)
    reference = np.ones((size, size), dtype=complex)
    
    # Hologram is interference pattern
    total_field = object_field + reference
    hologram = np.abs(total_field)**2
    
    # Add some noise
    noise = np.random.normal(0, 0.01 * np.max(hologram), hologram.shape)
    hologram += noise
    
    return np.maximum(hologram, 0)  # Ensure non-negative

print("Hologram processing functions defined!")`);
            container.appendChild(functionsCell);
            
            // Add demo cell
            const demoCell = createCell('code', `# Generate and display a sample hologram
sample_hologram = generate_sample_hologram(512)

plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.imshow(sample_hologram, cmap='gray')
plt.title('Sample Hologram')
plt.colorbar()

# Process the hologram
results = process_hologram(sample_hologram, distance=0.004)

plt.subplot(1, 3, 2)
plt.imshow(results['intensity'], cmap='hot')
plt.title('Reconstructed Intensity')
plt.colorbar()

plt.subplot(1, 3, 3)
plt.imshow(results['phase'], cmap='hsv')
plt.title('Reconstructed Phase')
plt.colorbar()

plt.tight_layout()
plt.show()

print(f'Hologram shape: {sample_hologram.shape}')
print(f'Intensity range: {results["intensity"].min():.2e} - {results["intensity"].max():.2e}')
print(f'Phase range: {results["phase"].min():.2f} - {results["phase"].max():.2f}')`);
            container.appendChild(demoCell);
        }
        
        // Initialize when page loads
        window.addEventListener('load', initPyodide);
    </script>
</body>
</html>'''
        
        # Write the main index.html
        with open(lab_dir / "index.html", 'w') as f:
            f.write(html_content)
            
        print(f"Created JupyterLite interface at {lab_dir / 'index.html'}")
        return True
            
    def build_site(self):
        """Build the JupyterLite site."""
        print("Building JupyterLite site...")
        
        # Create the HTML interface
        if not self.create_jupyterlite_html():
            return False
            
        print("JupyterLite site built successfully!")
        print(f"Output in: {self.output_dir / '_output'}")
        return True
            
    def copy_to_static(self, static_dir):
        """Copy built site to static directory."""
        built_site = self.output_dir / "_output"
        static_path = Path(static_dir)
        
        if not built_site.exists():
            print(f"Built site not found at {built_site}")
            return False
            
        # Remove existing jupyter files
        jupyter_static = static_path / "jupyter"
        if jupyter_static.exists():
            shutil.rmtree(jupyter_static)
            
        # Copy built site
        shutil.copytree(built_site, jupyter_static)
        print(f"JupyterLite site copied to {jupyter_static}")
        
        # Create simple index redirect
        index_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HoloBox Jupyter Notebook</title>
    <meta http-equiv="refresh" content="0; url=jupyter/lab/index.html">
</head>
<body>
    <p>Redirecting to <a href="jupyter/lab/index.html">HoloBox Jupyter Notebook</a>...</p>
</body>
</html>'''
        
        with open(static_path / "notebook.html", 'w') as f:
            f.write(index_content)
            
        print("Created notebook.html redirect")
        return True
        
    def build(self, static_dir=None):
        """Complete build process."""
        print(f"Building JupyterLite for HoloBox...")
        print(f"Output directory: {self.output_dir}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build site (no longer needs pip installation)
        if not self.build_site():
            return False
            
        # Copy to static directory if provided
        if static_dir:
            self.copy_to_static(static_dir)
            
        print("Build completed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Build JupyterLite for HoloBox')
    parser.add_argument('--output', '-o', default='./jupyter_build', 
                       help='Output directory for build (default: ./jupyter_build)')
    parser.add_argument('--static', '-s', 
                       help='Copy result to static directory')
    parser.add_argument('--clean', action='store_true',
                       help='Clean output directory before building')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    
    if args.clean and output_dir.exists():
        print(f"Cleaning {output_dir}...")
        shutil.rmtree(output_dir)
        
    builder = JupyterLiteBuilder(output_dir)
    
    if builder.build(args.static):
        print("\n✅ JupyterLite build successful!")
        if args.static:
            print(f"📁 Files available in: {args.static}")
            print(f"🌐 Access at: http://localhost:8000/static/notebook.html")
        else:
            print(f"📁 Files available in: {output_dir / '_output'}")
    else:
        print("\n❌ Build failed!")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())