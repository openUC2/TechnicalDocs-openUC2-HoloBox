// JavaScript-based hologram processing for offline use
// Simplified version that doesn't require PyScript/numpy

let processingEnabled = false;
let processingInterval = null;
let currentWavelength = 440; // nm
let currentPixelSize = 1.4; // µm
let currentDistance = 5.0; // mm

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if hologram processing elements exist
    if (document.getElementById('toggleProcessing')) {
        document.getElementById('toggleProcessing').onclick = toggleProcessing;
        document.getElementById('processFrame').onclick = processCurrentFrame;
        document.getElementById('toggleDebug').onclick = toggleDebugMode;
        
        // Parameter slider listeners
        document.getElementById('wavelength').oninput = updateParameters;
        document.getElementById('pixelsize').oninput = updateParameters;
        document.getElementById('dz').oninput = updateParameters;
        
        // Initial parameter update
        updateParameters();
        
        console.log('Hologram processing (offline mode) initialized');
    }
});

function updateParameters() {
    // Update wavelength
    currentWavelength = parseFloat(document.getElementById('wavelength').value);
    document.getElementById('wavelength-value').textContent = Math.round(currentWavelength);
    
    // Update pixel size
    currentPixelSize = parseFloat(document.getElementById('pixelsize').value);
    document.getElementById('pixelsize-value').textContent = currentPixelSize.toFixed(1);
    
    // Update distance
    currentDistance = parseFloat(document.getElementById('dz').value);
    document.getElementById('dz-value').textContent = currentDistance.toFixed(2);
    
    console.log(`Parameters updated: λ=${currentWavelength}nm, px=${currentPixelSize}µm, z=${currentDistance}mm`);
}

function toggleProcessing() {
    processingEnabled = !processingEnabled;
    
    if (processingEnabled) {
        // Start processing
        processingInterval = setInterval(processCurrentFrame, 1000); // Process every second
        document.getElementById('toggleProcessing').textContent = 'Disable Processing';
        document.getElementById('processing-enabled').textContent = 'Enabled (Offline Mode)';
        document.getElementById('status').textContent = 'Processing frames (simplified offline mode)...';
    } else {
        // Stop processing
        if (processingInterval) {
            clearInterval(processingInterval);
        }
        document.getElementById('toggleProcessing').textContent = 'Enable Processing';
        document.getElementById('processing-enabled').textContent = 'Disabled';
        document.getElementById('status').textContent = 'Processing stopped';
    }
}

function toggleDebugMode() {
    // Simple debug mode toggle
    const debugBtn = document.getElementById('toggleDebug');
    const debugStatus = document.getElementById('debug-status');
    
    if (debugStatus.textContent === 'Enabled') {
        debugBtn.textContent = 'Enable Debug';
        debugStatus.textContent = 'Disabled';
        console.log('Debug mode disabled');
    } else {
        debugBtn.textContent = 'Disable Debug';
        debugStatus.textContent = 'Enabled';
        console.log('Debug mode enabled');
    }
}

function processCurrentFrame() {
    // Simplified processing that works without numpy/scipy
    // This creates a simulated hologram effect using canvas manipulation
    
    const canvas = document.getElementById('processed');
    const ctx = canvas.getContext('2d');
    
    // Create a simple pattern based on current parameters
    const width = canvas.width;
    const height = canvas.height;
    
    // Create image data
    const imageData = ctx.createImageData(width, height);
    const data = imageData.data;
    
    // Generate a simple interference pattern as a demo
    const centerX = width / 2;
    const centerY = height / 2;
    const scale = currentDistance / 5.0; // Use distance parameter
    const freq = currentWavelength / 500.0; // Use wavelength parameter
    
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const dx = (x - centerX) * currentPixelSize;
            const dy = (y - centerY) * currentPixelSize;
            const r = Math.sqrt(dx * dx + dy * dy);
            
            // Simple interference pattern
            const intensity = Math.abs(Math.cos(r * freq * scale)) * 255;
            
            const index = (y * width + x) * 4;
            data[index] = intensity;     // Red
            data[index + 1] = intensity; // Green
            data[index + 2] = intensity; // Blue
            data[index + 3] = 255;       // Alpha
        }
    }
    
    // Put the processed image data on canvas
    ctx.putImageData(imageData, 0, 0);
    
    // Update status
    document.getElementById('last-processed').textContent = new Date().toLocaleTimeString();
    
    if (document.getElementById('debug-status').textContent === 'Enabled') {
        console.log(`Processed frame with parameters: λ=${currentWavelength}nm, px=${currentPixelSize}µm, z=${currentDistance}mm`);
    }
}