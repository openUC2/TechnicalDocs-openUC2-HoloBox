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

async function processCurrentFrame() {
    // Simplified processing that works without numpy/scipy
    // This creates a simulated hologram effect using canvas manipulation
    
    const canvas = document.getElementById('processed');
    const ctx = canvas.getContext('2d');
    const stream = document.getElementById('stream');
    
    // If we have a stream, try to process from snapshot API to avoid CORS issues
    if (stream && stream.complete && stream.naturalWidth > 0) {
        try {
            await processFromSnapshotAPI(ctx, canvas);
        } catch (error) {
            console.warn('Snapshot processing failed, using synthetic pattern');
            processFromSyntheticPattern(ctx, canvas);
        }
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



async function processFromSnapshotAPI(ctx, canvas) {
    try {
        // Get a snapshot from the API instead of using the stream directly
        const response = await fetch(window.baseUrl + '/snapshot');
        if (!response.ok) {
            throw new Error(`Snapshot API failed: ${response.status}`);
        }
        
        const blob = await response.blob();
        
        // Create an image from the blob
        const img = new Image();
        img.crossOrigin = 'anonymous'; // Enable CORS
        
        return new Promise((resolve, reject) => {
            img.onload = () => {
                try {
                    // Create temp canvas for processing
                    const tempCanvas = document.createElement('canvas');
                    const tempCtx = tempCanvas.getContext('2d');
                    tempCanvas.width = img.width;
                    tempCanvas.height = img.height;
                    
                    // Draw image to temp canvas
                    tempCtx.drawImage(img, 0, 0);
                    
                    // Apply transformations if needed
                    const orientation = processingSettings.orientation;
                    if (orientation.flipX || orientation.flipY || orientation.rotation !== 0) {
                        applyImageTransformations(tempCtx, tempCanvas, orientation);
                    }
                    
                    // Extract ROI from center
                    const roiSize = processingSettings.roi.size;
                    const centerX = Math.floor(tempCanvas.width * processingSettings.roi.centerX);
                    const centerY = Math.floor(tempCanvas.height * processingSettings.roi.centerY);
                    const startX = Math.max(0, centerX - roiSize / 2);
                    const startY = Math.max(0, centerY - roiSize / 2);
                    
                    const roiImageData = tempCtx.getImageData(startX, startY, roiSize, roiSize);
                    
                    // Process the image data
                    processImageData(ctx, canvas, roiImageData, roiSize);
                    
                    resolve();
                } catch (error) {
                    console.warn('Error processing snapshot:', error);
                    processFromSyntheticPattern(ctx, canvas);
                    reject(error);
                }
            };
            
            img.onerror = () => {
                console.warn('Failed to load snapshot image');
                processFromSyntheticPattern(ctx, canvas);
                reject(new Error('Failed to load snapshot'));
            };
            
            // Set the image source to the blob URL
            img.src = URL.createObjectURL(blob);
        });
        
    } catch (error) {
        console.warn('Could not fetch snapshot, falling back to synthetic pattern:', error);
        processFromSyntheticPattern(ctx, canvas);
    }
}

function applyImageTransformations(ctx, canvas, orientation) {
    // Apply CSS-like transformations to canvas context
    const { width, height } = canvas;
    
    // Save the current context state
    ctx.save();
    
    // Move to center for transformations
    ctx.translate(width / 2, height / 2);
    
    // Apply rotation
    if (orientation.rotation !== 0) {
        ctx.rotate((orientation.rotation * Math.PI) / 180);
    }
    
    // Apply scaling for flips
    let scaleX = 1;
    let scaleY = 1;
    
    if (orientation.flipX) scaleX = -1;
    if (orientation.flipY) scaleY = -1;
    
    if (scaleX !== 1 || scaleY !== 1) {
        ctx.scale(scaleX, scaleY);
    }
    
    // Get the current image data
    ctx.restore();
    // Note: This is a simplified approach - full transformation would require 
    // redrawing the image with proper matrix transformations
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