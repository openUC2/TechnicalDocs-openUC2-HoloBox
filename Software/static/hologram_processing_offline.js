// JavaScript-based hologram processing for offline use
// Simplified version that doesn't require PyScript/numpy

let processingEnabled = false;
let processingInterval = null;
let currentWavelength = 440; // nm
let currentPixelSize = 1.4; // µm
let currentDistance = 5.0; // mm

// Processing settings
let processingSettings = {
    orientation: {
        flipX: false,
        flipY: false,
        rotation: 0
    },
    roi: {
        size: 256,
        centerX: 0.5,
        centerY: 0.5
    },
    processing: {
        colorChannel: 'green'
    }
};

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
    const stream = document.getElementById('stream');
    
    // If we have a stream, try to process from actual camera data
    if (stream && stream.complete && stream.naturalWidth > 0) {
        processFromCameraStream(ctx, canvas, stream);
    } else {
        // Fallback to synthetic pattern
        processFromSyntheticPattern(ctx, canvas);
    }
    
    // Update status
    document.getElementById('last-processed').textContent = new Date().toLocaleTimeString();
    
    if (document.getElementById('debug-status').textContent === 'Enabled') {
        console.log(`Processed frame with parameters: λ=${currentWavelength}nm, px=${currentPixelSize}µm, z=${currentDistance}mm`);
        console.log(`Processing settings: channel=${processingSettings.processing.colorChannel}, ROI=${processingSettings.roi.size}x${processingSettings.roi.size}, rotation=${processingSettings.orientation.rotation}°`);
    }
}

function processFromCameraStream(ctx, canvas, stream) {
    const width = canvas.width;
    const height = canvas.height;
    
    // Create a temporary canvas to draw and extract from the camera stream
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = stream.naturalWidth;
    tempCanvas.height = stream.naturalHeight;
    
    // Draw the camera stream onto temp canvas
    tempCtx.drawImage(stream, 0, 0);
    
    // Extract ROI from center of image
    const roiSize = processingSettings.roi.size;
    const centerX = Math.floor(tempCanvas.width * processingSettings.roi.centerX);
    const centerY = Math.floor(tempCanvas.height * processingSettings.roi.centerY);
    const startX = Math.max(0, centerX - roiSize / 2);
    const startY = Math.max(0, centerY - roiSize / 2);
    
    try {
        const roiImageData = tempCtx.getImageData(startX, startY, roiSize, roiSize);
        
        // Process with color channel selection and orientation
        processImageData(ctx, canvas, roiImageData, roiSize);
    } catch (e) {
        console.warn('Could not process camera stream, falling back to synthetic pattern:', e);
        processFromSyntheticPattern(ctx, canvas);
    }
}

function processFromSyntheticPattern(ctx, canvas) {
    // Create a simple pattern based on current parameters (fallback)
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
}

function processImageData(ctx, canvas, imageData, sourceSize) {
    const data = imageData.data;
    const width = canvas.width;
    const height = canvas.height;
    
    // Create output image data
    const outputData = ctx.createImageData(width, height);
    const output = outputData.data;
    
    // Get color channel multipliers
    let rMult = 0, gMult = 0, bMult = 0;
    switch (processingSettings.processing.colorChannel) {
        case 'red': rMult = 1; break;
        case 'green': gMult = 1; break;
        case 'blue': bMult = 1; break;
    }
    
    // Process each pixel with hologram reconstruction simulation
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            // Map output coordinates to source ROI coordinates
            const srcX = Math.floor((x / width) * sourceSize);
            const srcY = Math.floor((y / height) * sourceSize);
            
            if (srcX < sourceSize && srcY < sourceSize) {
                // Apply rotation transformation on source coordinates
                let finalX = srcX, finalY = srcY;
                const centerX = sourceSize / 2;
                const centerY = sourceSize / 2;
                
                if (processingSettings.orientation.rotation !== 0) {
                    const angle = (processingSettings.orientation.rotation * Math.PI) / 180;
                    const relX = srcX - centerX;
                    const relY = srcY - centerY;
                    finalX = Math.floor(centerX + relX * Math.cos(angle) - relY * Math.sin(angle));
                    finalY = Math.floor(centerY + relX * Math.sin(angle) + relY * Math.cos(angle));
                }
                
                // Apply flip transformations
                if (processingSettings.orientation.flipX) {
                    finalX = sourceSize - 1 - finalX;
                }
                if (processingSettings.orientation.flipY) {
                    finalY = sourceSize - 1 - finalY;
                }
                
                // Bounds check
                if (finalX >= 0 && finalX < sourceSize && finalY >= 0 && finalY < sourceSize) {
                    const srcIndex = (finalY * sourceSize + finalX) * 4;
                    const outIndex = (y * width + x) * 4;
                    
                    // Extract selected color channel
                    const r = data[srcIndex];
                    const g = data[srcIndex + 1];
                    const b = data[srcIndex + 2];
                    
                    const intensity = r * rMult + g * gMult + b * bMult;
                    
                    // Simple hologram effect - phase modulation based on distance
                    const dx = (x - width/2) * currentPixelSize;
                    const dy = (y - height/2) * currentPixelSize;
                    const phase = Math.sqrt(dx*dx + dy*dy) * currentDistance / currentWavelength;
                    const modulated = intensity * (0.5 + 0.5 * Math.cos(phase));
                    
                    output[outIndex] = modulated;
                    output[outIndex + 1] = modulated;
                    output[outIndex + 2] = modulated;
                    output[outIndex + 3] = 255;
                }
            }
        }
    }
    
    ctx.putImageData(outputData, 0, 0);
}

// Update processing settings function (called from camera_controls.js)
window.updateHologramProcessingSettings = function(settings) {
    processingSettings = { ...processingSettings, ...settings };
    console.log('Hologram processing settings updated:', processingSettings);
};