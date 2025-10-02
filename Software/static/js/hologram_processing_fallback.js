/**
 * JavaScript Fallback for Hologram Processing
 * 
 * This file provides a pure JavaScript implementation of hologram processing
 * for devices where PyScript/Pyodide is not available (e.g., iOS/iPadOS).
 * 
 * Functions are designed to match the Python API 1:1 for seamless fallback.
 */

// Import FFT library (we'll use a simple FFT implementation or library)
// For now, using a simplified approach without full FFT for basic functionality

class HologramProcessorFallback {
    constructor() {
        this.processingEnabled = false;
        this.processingInterval = null;
        this.currentWavelength = 440e-9;  // nm to m
        this.currentPixelsize = 1.4e-6;   // µm to m
        this.currentDz = 0.005;           // mm to m
        this.debugMode = true;
        
        console.log("🔧 Starting JavaScript fallback hologram processing setup...");
    }

    /**
     * Calculate intensity (what a detector sees)
     */
    abssqr(complexArray) {
        // For real arrays, just square them
        const result = new Float64Array(complexArray.length);
        for (let i = 0; i < complexArray.length; i++) {
            result[i] = complexArray[i] * complexArray[i];
        }
        return result;
    }

    /**
     * Simple 2D Fourier Transform (simplified version)
     * Note: Full FFT would require a library like fft.js
     */
    FT(data, width, height) {
        console.warn("⚠️ Full FFT not implemented in fallback mode - using simplified processing");
        // Return input for now - in production, would use a proper FFT library
        return data;
    }

    /**
     * Simple inverse Fourier Transform (simplified version)
     */
    iFT(data, width, height) {
        console.warn("⚠️ Full inverse FFT not implemented in fallback mode - using simplified processing");
        return data;
    }

    /**
     * Fresnel propagator (simplified version without FFT)
     */
    fresnelPropagator(E0, ps, lambda0, z, width, height) {
        console.warn("⚠️ Fresnel propagation simplified in fallback mode");
        // Return input with minimal processing
        return E0;
    }

    /**
     * Apply image transformations (flip and rotation)
     */
    applyImageTransformations(imageData, flipX, flipY, rotation, width, height) {
        const pixels = new Uint8ClampedArray(imageData);
        const result = new Uint8ClampedArray(pixels.length);
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                let srcX = x;
                let srcY = y;
                
                // Apply flips
                if (flipX) srcX = width - 1 - x;
                if (flipY) srcY = height - 1 - y;
                
                // Apply rotation
                let finalX = srcX;
                let finalY = srcY;
                
                if (rotation === 90) {
                    finalX = srcY;
                    finalY = width - 1 - srcX;
                } else if (rotation === 180) {
                    finalX = width - 1 - srcX;
                    finalY = height - 1 - srcY;
                } else if (rotation === 270) {
                    finalX = height - 1 - srcY;
                    finalY = srcX;
                }
                
                // Copy pixel data (RGBA)
                const srcIdx = (srcY * width + srcX) * 4;
                const dstIdx = (y * width + x) * 4;
                
                if (srcIdx >= 0 && srcIdx < pixels.length - 3) {
                    result[dstIdx] = pixels[srcIdx];
                    result[dstIdx + 1] = pixels[srcIdx + 1];
                    result[dstIdx + 2] = pixels[srcIdx + 2];
                    result[dstIdx + 3] = pixels[srcIdx + 3];
                }
            }
        }
        
        return result;
    }

    /**
     * Get ROI coordinates from boundary box
     */
    getRoiCoordinates(imgWidth, imgHeight, roiSize, flipX, flipY, rotation) {
        try {
            if (window.getBoundaryBoxCoordinates) {
                const bboxCoords = window.getBoundaryBoxCoordinates();
                
                let startX = parseInt(bboxCoords.start_x || 0);
                let startY = parseInt(bboxCoords.start_y || 0);
                let endX = parseInt(bboxCoords.end_x || imgWidth);
                let endY = parseInt(bboxCoords.end_y || imgHeight);
                
                // Scale coordinates if needed
                const streamImg = document.getElementById('stream');
                if (streamImg && streamImg.naturalWidth > 0) {
                    const scaleX = imgWidth / streamImg.naturalWidth;
                    const scaleY = imgHeight / streamImg.naturalHeight;
                    
                    startX = Math.floor(startX * scaleX);
                    startY = Math.floor(startY * scaleY);
                    endX = Math.floor(endX * scaleX);
                    endY = Math.floor(endY * scaleY);
                }
                
                // Ensure bounds
                startX = Math.max(0, Math.min(startX, imgWidth));
                startY = Math.max(0, Math.min(startY, imgHeight));
                endX = Math.max(startX + 1, Math.min(endX, imgWidth));
                endY = Math.max(startY + 1, Math.min(endY, imgHeight));
                
                return {
                    start_x: startX,
                    start_y: startY,
                    end_x: endX,
                    end_y: endY,
                    width: endX - startX,
                    height: endY - startY
                };
            }
        } catch (e) {
            if (this.debugMode) {
                console.log(`Debug: Error getting boundary box coordinates: ${e}`);
            }
        }
        
        // Fallback to center crop
        const centerX = Math.floor(imgWidth / 2);
        const centerY = Math.floor(imgHeight / 2);
        const startX = Math.max(0, centerX - Math.floor(roiSize / 2));
        const startY = Math.max(0, centerY - Math.floor(roiSize / 2));
        const endX = Math.min(imgWidth, startX + roiSize);
        const endY = Math.min(imgHeight, startY + roiSize);
        
        return {
            start_x: startX,
            start_y: startY,
            end_x: endX,
            end_y: endY,
            width: endX - startX,
            height: endY - startY
        };
    }

    /**
     * Main image processing function (simplified without full holographic reconstruction)
     */
    processImageForHologram() {
        try {
            if (this.debugMode) {
                console.log("🔄 [Fallback] Processing image...");
            }

            // Get the camera stream
            const streamImg = document.getElementById('stream');
            if (!streamImg || !streamImg.complete || streamImg.naturalWidth === 0) {
                console.log("⚠️ Stream not ready");
                return;
            }

            // Create temporary canvas to get image data
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');
            
            const actualWidth = streamImg.naturalWidth;
            const actualHeight = streamImg.naturalHeight;
            
            tempCanvas.width = actualWidth;
            tempCanvas.height = actualHeight;
            
            // Draw the stream image
            tempCtx.drawImage(streamImg, 0, 0);
            const imageData = tempCtx.getImageData(0, 0, actualWidth, actualHeight);
            
            // Get settings from interface
            const flipX = document.getElementById('flipX')?.checked || false;
            const flipY = document.getElementById('flipY')?.checked || false;
            const rotation = parseInt(document.getElementById('rotationAngle')?.value || 0);
            const roiSize = parseInt(document.getElementById('roiSize')?.value || 256);
            const colorChannel = document.getElementById('colorChannel')?.value || 'green';
            
            // Extract color channel
            const pixels = imageData.data;
            const grayData = new Float64Array(actualWidth * actualHeight);
            
            let channelIndex = 1; // green
            if (colorChannel === 'red') channelIndex = 0;
            else if (colorChannel === 'blue') channelIndex = 2;
            
            for (let i = 0; i < grayData.length; i++) {
                grayData[i] = pixels[i * 4 + channelIndex] / 255.0;
            }
            
            // Get ROI coordinates
            const roiCoords = this.getRoiCoordinates(actualWidth, actualHeight, roiSize, flipX, flipY, rotation);
            
            // Extract ROI
            const roiWidth = roiCoords.width;
            const roiHeight = roiCoords.height;
            const roiData = new Float64Array(roiWidth * roiHeight);
            
            for (let y = 0; y < roiHeight; y++) {
                for (let x = 0; x < roiWidth; x++) {
                    const srcX = roiCoords.start_x + x;
                    const srcY = roiCoords.start_y + y;
                    const srcIdx = srcY * actualWidth + srcX;
                    const dstIdx = y * roiWidth + x;
                    
                    if (srcIdx < grayData.length) {
                        roiData[dstIdx] = grayData[srcIdx];
                    }
                }
            }
            
            // Apply simplified processing (without full FFT-based holographic reconstruction)
            // Just show the intensity with basic enhancement
            const processedData = new Uint8ClampedArray(roiWidth * roiHeight * 4);
            
            for (let i = 0; i < roiData.length; i++) {
                const intensity = Math.floor(roiData[i] * 255);
                processedData[i * 4] = intensity;
                processedData[i * 4 + 1] = intensity;
                processedData[i * 4 + 2] = intensity;
                processedData[i * 4 + 3] = 255;
            }
            
            // Display processed image
            const processedCanvas = document.getElementById('processed');
            if (processedCanvas) {
                processedCanvas.width = roiWidth;
                processedCanvas.height = roiHeight;
                
                const ctx = processedCanvas.getContext('2d');
                const outputImageData = new ImageData(processedData, roiWidth, roiHeight);
                ctx.putImageData(outputImageData, 0, 0);
            }
            
            // Update status
            const timestamp = new Date().toLocaleTimeString();
            const statusElem = document.getElementById('last-processed');
            if (statusElem) {
                statusElem.textContent = `${timestamp} (Fallback Mode)`;
            }
            
        } catch (e) {
            console.error("❌ Error in fallback processing:", e);
        }
    }

    /**
     * Update parameters from sliders
     */
    updateParameters(event = null) {
        try {
            const wavelengthElem = document.getElementById('wavelength');
            if (wavelengthElem) {
                this.currentWavelength = parseFloat(wavelengthElem.value) * 1e-9;
            }
            
            const pixelsizeElem = document.getElementById('pixelsize');
            if (pixelsizeElem) {
                this.currentPixelsize = parseFloat(pixelsizeElem.value) * 1e-6;
            }
            
            const dzElem = document.getElementById('dz');
            if (dzElem) {
                this.currentDz = parseFloat(dzElem.value) * 0.001;
            }
            
            if (this.debugMode) {
                console.log(`📐 [Fallback] Parameters updated: λ=${(this.currentWavelength * 1e9).toFixed(0)}nm, px=${(this.currentPixelsize * 1e6).toFixed(1)}µm, z=${(this.currentDz * 1000).toFixed(1)}mm`);
            }
        } catch (e) {
            console.error("❌ Error updating parameters:", e);
        }
    }

    /**
     * Toggle processing on/off
     */
    toggleProcessing(event = null) {
        this.processingEnabled = !this.processingEnabled;
        
        const toggleBtn = document.getElementById('toggleProcessing');
        const statusElem = document.getElementById('processing-enabled');
        
        if (this.processingEnabled) {
            if (toggleBtn) {
                toggleBtn.textContent = 'Disable Processing';
                toggleBtn.className = 'btn btn-danger';
            }
            if (statusElem) statusElem.textContent = 'Enabled (Fallback Mode)';
            
            // Start processing at intervals
            this.processingInterval = setInterval(() => {
                this.processImageForHologram();
            }, 100);
            
            console.log("✅ [Fallback] Processing enabled");
        } else {
            if (toggleBtn) {
                toggleBtn.textContent = 'Enable Processing';
                toggleBtn.className = 'btn btn-success';
            }
            if (statusElem) statusElem.textContent = 'Disabled';
            
            if (this.processingInterval) {
                clearInterval(this.processingInterval);
                this.processingInterval = null;
            }
            
            console.log("⏸️ [Fallback] Processing disabled");
        }
    }

    /**
     * Process a single frame
     */
    processSingleFrame(event = null) {
        console.log("🔄 [Fallback] Processing single frame...");
        this.processImageForHologram();
    }

    /**
     * Toggle debug mode
     */
    toggleDebugMode(event = null) {
        this.debugMode = !this.debugMode;
        
        const debugBtn = document.getElementById('toggleDebug');
        if (debugBtn) {
            if (this.debugMode) {
                debugBtn.textContent = 'Disable Debug';
                debugBtn.className = 'btn btn-warning';
                console.log("🐛 [Fallback] Debug mode enabled");
            } else {
                debugBtn.textContent = 'Enable Debug';
                debugBtn.className = 'btn btn-outline-warning';
                console.log("🐛 [Fallback] Debug mode disabled");
            }
        }
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Processing controls
        const toggleBtn = document.getElementById('toggleProcessing');
        if (toggleBtn) {
            toggleBtn.onclick = (e) => this.toggleProcessing(e);
        }

        const singleFrameBtn = document.getElementById('processSingleFrame');
        if (singleFrameBtn) {
            singleFrameBtn.onclick = (e) => this.processSingleFrame(e);
        }

        const debugBtn = document.getElementById('toggleDebug');
        if (debugBtn) {
            debugBtn.onclick = (e) => this.toggleDebugMode(e);
        }

        // Parameter sliders
        const wavelengthSlider = document.getElementById('wavelength');
        if (wavelengthSlider) {
            wavelengthSlider.oninput = (e) => this.updateParameters(e);
        }

        const pixelsizeSlider = document.getElementById('pixelsize');
        if (pixelsizeSlider) {
            pixelsizeSlider.oninput = (e) => this.updateParameters(e);
        }

        const dzSlider = document.getElementById('dz');
        if (dzSlider) {
            dzSlider.oninput = (e) => this.updateParameters(e);
        }

        // Initial parameter update
        this.updateParameters();

        console.log("✅ [Fallback] Event listeners initialized");

        // Test with a single frame
        this.processImageForHologram();
    }
}

// Export for use in fallback loader
window.HologramProcessorFallback = HologramProcessorFallback;
