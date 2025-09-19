// JavaScript for camera controls
let baseUrl = location.origin;

// Make baseUrl available globally for PyScript
window.baseUrl = baseUrl;

document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners once DOM is loaded
    document.getElementById('startBtn').onclick = startStream;
    document.getElementById('stopBtn').onclick = stopStream;
    document.getElementById('setExposure').onclick = setExposure;
    document.getElementById('setGain').onclick = setGain;
    document.getElementById('captureBtn').onclick = capture;
    
    // New camera controls
    document.getElementById('loadStatus').onclick = loadCameraStatus;
    document.getElementById('setResolution').onclick = setResolution;
    document.getElementById('setColorMode').onclick = setColorMode;
    document.getElementById('set-manual-exposure').onclick = setManualExposure;
    document.getElementById('set-awb-gains').onclick = setAWBGains;
    
    // Auto/Manual toggles
    document.getElementById('exposure-auto').onchange = function() {
        setExposureMode(this.checked);
    };
    document.getElementById('awb-auto').onchange = function() {
        setAWBMode(this.checked);
    };
    
    // WiFi management event listeners
    document.getElementById('refreshStatus').onclick = refreshWifiStatus;
    document.getElementById('scanNetworks').onclick = scanNetworks;
    document.getElementById('enableAP').onclick = enableAccessPoint;
    document.getElementById('connectWifi').onclick = connectToWifi;
    
    // Image orientation controls
    document.getElementById('flipX').onchange = updateImageOrientation;
    document.getElementById('flipY').onchange = updateImageOrientation;
    document.getElementById('rotationAngle').onchange = updateImageOrientation;
    
    // Processing options
    document.getElementById('roiSize').onchange = updateBoundaryBox;
    document.getElementById('colorChannel').onchange = updateProcessingSettings;
    
    // Boundary box control
    document.getElementById('showBoundaryBox').onchange = toggleBoundaryBox;
    
    // URL input change listener for user edits
    document.getElementById('host').onchange = updateBaseUrl;
    document.getElementById('host').oninput = updateBaseUrl;
    
    // Auto-detect URL from browser location (initial suggestion only)
    initializeAutoDetectedUrl();
    
    // Initialize
    document.getElementById('status').textContent = 'Ready - Click Start Stream to begin';
    refreshWifiStatus(); // Load initial WiFi status
    loadCameraStatus(); // Load initial camera status
    
    // Initialize processing canvas to square aspect ratio
    initializeProcessedCanvas();
});

// Auto-detect URL from browser location (initial suggestion only)
const initializeAutoDetectedUrl = () => {
    const hostInput = document.getElementById('host');
    const currentHost = window.location.hostname;
    const currentPort = window.location.port;
    
    // Always use HTTP as requested by user
    let detectedUrl;
    
    // If we're accessing via specific host, use current host with port 80
    if (currentHost !== '127.0.0.1') {
        detectedUrl = currentPort && currentPort !== '80' 
            ? `http://${currentHost}:${currentPort}` 
            : `http://${currentHost}`;
    } else {
        // Default fallback for local development
        detectedUrl = 'http://192.168.4.1';
    }
    
    // Only set the value if the field is empty (initial load)
    if (!hostInput.value.trim()) {
        hostInput.value = detectedUrl;
    }
    
    // Update baseUrl from whatever is in the field
    updateBaseUrl();
    
    console.log('Auto-detected API URL:', baseUrl);
};

// Update baseUrl when user changes the host input
const updateBaseUrl = () => {
    const hostInput = document.getElementById('host');
    const newUrl = hostInput.value.trim();
    
    if (newUrl) {
        baseUrl = newUrl.replace(/\/+$/, ''); // Remove trailing slashes
        window.baseUrl = baseUrl;
        console.log('Updated API URL to:', baseUrl);
    }
};

const api = (path, opt = {}) => {
    // Add timeout for better mobile reliability
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 10000); // 10 second timeout
    });
    
    const fetchPromise = fetch(baseUrl + path, {
        ...opt,
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            ...opt.headers
        }
    });
    
    return Promise.race([fetchPromise, timeoutPromise]);
};

const startStream = () => {
    const stream = document.getElementById('stream');
    // Use the more compatible MJPEG stream endpoint
    stream.src = baseUrl + '/api/stream.mjpg';
    
    // Add timestamp to prevent caching issues on mobile
    const timestamp = new Date().getTime();
    stream.src += '?t=' + timestamp;
    
    stream.onload = () => {
        updateStreamAspectRatio();
        if (!document.getElementById('boundary-box').classList.contains('hidden')) {
            updateBoundaryBox();
        }
        document.getElementById('status').textContent = 'Stream started';
        console.log('Stream loaded successfully');
    };
    
    // Handle error for better debugging
    stream.onerror = () => {
        document.getElementById('status').textContent = 'Stream failed to load - check connection';
        console.error('Stream failed to load from:', stream.src);
        
        // On mobile devices, suggest manual refresh
        if (/iPad|iPhone|iPod|Android/i.test(navigator.userAgent)) {
            setTimeout(() => {
                document.getElementById('status').textContent = 'Stream error - try tapping the image area or refresh page';
            }, 2000);
        }
    };
    
    // Handle abort (common on mobile when switching networks)
    stream.onabort = () => {
        console.log('Stream loading aborted');
        document.getElementById('status').textContent = 'Stream loading interrupted';
    };
    
    // Add click handler for mobile devices to retry loading
    stream.onclick = () => {
        if (!stream.complete || stream.naturalWidth === 0) {
            console.log('Retrying stream load due to user tap');
            const currentSrc = stream.src.split('?')[0]; // Remove timestamp
            stream.src = currentSrc + '?t=' + new Date().getTime();
        }
    };
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (!document.getElementById('boundary-box').classList.contains('hidden')) {
            updateBoundaryBox();
        }
    });
    
    console.log('Starting stream from:', stream.src);
};

const stopStream = () => {
    document.getElementById('stream').removeAttribute('src');
    document.getElementById('status').textContent = 'Stream stopped';
};

const setExposure = () => {
    const v = parseInt(document.getElementById('exposure').value, 10);
    if (!isNaN(v)) {
        api('/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({exposure_us: v})
        }).then(r => r.json()).then(data => {
            console.log('Exposure set:', data);
            document.getElementById('status').textContent = `Exposure set to ${v}µs`;
        });
    }
};

const setGain = () => {
    const v = parseFloat(document.getElementById('gain').value);
    if (!isNaN(v)) {
        api('/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({gain: v})
        }).then(r => r.json()).then(data => {
            console.log('Gain set:', data);
            document.getElementById('status').textContent = `Gain set to ${v}`;
        });
    }
};

const capture = () => {
    const link = document.getElementById('downloadLink');
    link.classList.add('d-none');
    api('/snapshot')
        .then(r => r.blob())
        .then(b => {
            link.href = URL.createObjectURL(b);
            link.classList.remove('d-none');
            document.getElementById('status').textContent = 'Image captured';
        });
};

// New Camera Control Functions
const setExposureMode = (auto) => {
    api('/api/camera/exposure_mode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({auto: auto})
    }).then(r => r.json()).then(data => {
        console.log('Exposure mode set:', data);
        document.getElementById('status').textContent = `Exposure mode: ${auto ? 'Auto' : 'Manual'}`;
        updateCameraControlsUI();
    }).catch(err => {
        console.error('Error setting exposure mode:', err);
        document.getElementById('status').textContent = 'Error setting exposure mode';
    });
};

const setManualExposure = () => {
    const exposure = parseInt(document.getElementById('manual-exposure').value, 10);
    const gain = parseFloat(document.getElementById('manual-gain').value);
    
    if (isNaN(exposure) || isNaN(gain)) {
        document.getElementById('status').textContent = 'Invalid exposure or gain values';
        return;
    }
    
    api('/api/camera/exposure', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({exposure_us: exposure, analogue_gain: gain})
    }).then(r => r.json()).then(data => {
        console.log('Manual exposure set:', data);
        document.getElementById('status').textContent = `Manual exposure: ${data.exposure_us}µs, gain: ${data.analogue_gain}`;
    }).catch(err => {
        console.error('Error setting manual exposure:', err);
        document.getElementById('status').textContent = 'Error setting manual exposure';
    });
};

const setResolution = () => {
    const resSelect = document.getElementById('resolution-select');
    const [width, height] = resSelect.value.split('x').map(v => parseInt(v, 10));
    
    api('/api/camera/resolution', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({width: width, height: height})
    }).then(r => r.json()).then(data => {
        console.log('Resolution set:', data);
        document.getElementById('status').textContent = `Resolution: ${data.width}x${data.height}`;
        // Restart stream to apply new resolution
        setTimeout(() => {
            const stream = document.getElementById('stream');
            const currentSrc = stream.src;
            stream.src = '';
            setTimeout(() => {
                stream.src = currentSrc;
            }, 100);
        }, 500);
    }).catch(err => {
        console.error('Error setting resolution:', err);
        document.getElementById('status').textContent = 'Error setting resolution';
    });
};

const setAWBMode = (auto) => {
    api('/api/camera/awb_mode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({auto: auto})
    }).then(r => r.json()).then(data => {
        console.log('AWB mode set:', data);
        document.getElementById('status').textContent = `White balance: ${auto ? 'Auto' : 'Manual'}`;
        updateCameraControlsUI();
    }).catch(err => {
        console.error('Error setting AWB mode:', err);
        document.getElementById('status').textContent = 'Error setting AWB mode';
    });
};

const setAWBGains = () => {
    const red = parseFloat(document.getElementById('awb-red').value);
    const blue = parseFloat(document.getElementById('awb-blue').value);
    
    if (isNaN(red) || isNaN(blue)) {
        document.getElementById('status').textContent = 'Invalid white balance gain values';
        return;
    }
    
    api('/api/camera/awb_gains', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({red: red, blue: blue})
    }).then(r => r.json()).then(data => {
        console.log('AWB gains set:', data);
        document.getElementById('status').textContent = `WB gains - Red: ${data.red}, Blue: ${data.blue}`;
    }).catch(err => {
        console.error('Error setting AWB gains:', err);
        document.getElementById('status').textContent = 'Error setting AWB gains';
    });
};

const setColorMode = () => {
    const mode = document.getElementById('color-mode-select').value;
    
    api('/api/camera/color', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode: mode})
    }).then(r => r.json()).then(data => {
        console.log('Color mode set:', data);
        document.getElementById('status').textContent = `Color mode: ${data.color_mode}`;
    }).catch(err => {
        console.error('Error setting color mode:', err);
        document.getElementById('status').textContent = 'Error setting color mode';
    });
};

const loadCameraStatus = () => {
    api('/api/camera/status')
        .then(r => r.json())
        .then(data => {
            console.log('Camera status:', data);
            updateUIFromStatus(data);
        })
        .catch(err => {
            console.error('Error loading camera status:', err);
        });
};

const updateUIFromStatus = (status) => {
    // Update exposure controls
    if (document.getElementById('exposure-auto')) {
        document.getElementById('exposure-auto').checked = status.exposure_auto;
    }
    if (document.getElementById('manual-exposure')) {
        document.getElementById('manual-exposure').value = status.exposure_us;
    }
    if (document.getElementById('manual-gain')) {
        document.getElementById('manual-gain').value = status.analogue_gain;
    }
    
    // Update AWB controls
    if (document.getElementById('awb-auto')) {
        document.getElementById('awb-auto').checked = status.awb_auto;
    }
    if (document.getElementById('awb-red')) {
        document.getElementById('awb-red').value = status.awb_gains.red;
    }
    if (document.getElementById('awb-blue')) {
        document.getElementById('awb-blue').value = status.awb_gains.blue;
    }
    
    // Update resolution
    if (document.getElementById('resolution-select')) {
        const resValue = `${status.resolution.width}x${status.resolution.height}`;
        document.getElementById('resolution-select').value = resValue;
    }
    
    // Update color mode
    if (document.getElementById('color-mode-select')) {
        document.getElementById('color-mode-select').value = status.color_mode;
    }
    
    updateCameraControlsUI();
};

const updateCameraControlsUI = () => {
    // Enable/disable manual controls based on auto modes
    const exposureAuto = document.getElementById('exposure-auto')?.checked ?? true;
    const awbAuto = document.getElementById('awb-auto')?.checked ?? true;
    
    // Exposure controls
    if (document.getElementById('manual-exposure')) {
        document.getElementById('manual-exposure').disabled = exposureAuto;
    }
    if (document.getElementById('manual-gain')) {
        document.getElementById('manual-gain').disabled = exposureAuto;
    }
    if (document.getElementById('set-manual-exposure')) {
        document.getElementById('set-manual-exposure').disabled = exposureAuto;
    }
    
    // AWB controls
    if (document.getElementById('awb-red')) {
        document.getElementById('awb-red').disabled = awbAuto;
    }
    if (document.getElementById('awb-blue')) {
        document.getElementById('awb-blue').disabled = awbAuto;
    }
    if (document.getElementById('set-awb-gains')) {
        document.getElementById('set-awb-gains').disabled = awbAuto;
    }
};

// WiFi Management Functions
const refreshWifiStatus = () => {
    api('/wifi/status')
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                document.getElementById('wifi-status').innerHTML = 
                    `<span class="text-danger">Error: ${data.error}</span>`;
                return;
            }
            
            let statusHtml = '';
            if (data.is_access_point) {
                statusHtml = `<span class="text-warning">Access Point Mode</span><br>`;
            } else if (data.connected_ssid) {
                statusHtml = `<span class="text-success">Connected to: ${data.connected_ssid}</span><br>`;
            } else {
                statusHtml = `<span class="text-secondary">Not connected</span><br>`;
            }
            
            if (data.ip_address) {
                statusHtml += `IP: ${data.ip_address}<br>`;
            }
            statusHtml += `Interface: ${data.interface || 'wlan0'}`;
            
            document.getElementById('wifi-status').innerHTML = statusHtml;
        })
        .catch(err => {
            document.getElementById('wifi-status').innerHTML = 
                `<span class="text-danger">Error loading status</span>`;
            console.error('WiFi status error:', err);
        });
};

const scanNetworks = () => {
    document.getElementById('network-list').innerHTML = 
        '<small class="text-muted">Scanning...</small>';
    
    api('/wifi/scan')
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                document.getElementById('network-list').innerHTML = 
                    `<span class="text-danger">Error: ${data.error}</span>`;
                return;
            }
            
            if (!data.networks || data.networks.length === 0) {
                document.getElementById('network-list').innerHTML = 
                    '<small class="text-muted">No networks found</small>';
                return;
            }
            
            let html = '';
            data.networks.forEach(network => {
                const lockIcon = network.encrypted ? '🔒' : '📶';
                const quality = network.quality || 'Unknown';
                html += `
                    <div class="border-bottom py-2 network-item text-light" 
                         style="cursor: pointer; border-color: var(--bs-border-color-translucent) !important;" 
                         onclick="selectNetwork('${network.ssid}')">
                        <div class="d-flex justify-content-between">
                            <span>${lockIcon} ${network.ssid}</span>
                            <small class="text-muted">Quality: ${quality}</small>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('network-list').innerHTML = html;
        })
        .catch(err => {
            document.getElementById('network-list').innerHTML = 
                '<span class="text-danger">Error scanning networks</span>';
            console.error('Network scan error:', err);
        });
};

const selectNetwork = (ssid) => {
    document.getElementById('wifi-ssid').value = ssid;
};

const connectToWifi = () => {
    const ssid = document.getElementById('wifi-ssid').value.trim();
    const password = document.getElementById('wifi-password').value;
    
    if (!ssid) {
        alert('Please enter a network name (SSID)');
        return;
    }
    
    if (!password) {
        alert('Please enter a password');
        return;
    }
    
    document.getElementById('connectWifi').disabled = true;
    document.getElementById('connectWifi').textContent = 'Connecting...';
    
    api('/wifi/connect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ssid: ssid, password: password})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert(`Connection failed: ${data.error}`);
        } else {
            alert(`${data.message}\n\nThe system will need to be rebooted to connect to the new network.`);
            // Clear password field for security
            document.getElementById('wifi-password').value = '';
        }
    })
    .catch(err => {
        alert('Connection request failed. Please try again.');
        console.error('WiFi connect error:', err);
    })
    .finally(() => {
        document.getElementById('connectWifi').disabled = false;
        document.getElementById('connectWifi').textContent = 'Connect';
    });
};

const enableAccessPoint = () => {
    if (!confirm('This will enable Access Point mode and require a reboot. Continue?')) {
        return;
    }
    
    document.getElementById('enableAP').disabled = true;
    document.getElementById('enableAP').textContent = 'Configuring...';
    
    api('/wifi/access_point', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert(`Access Point setup failed: ${data.error}`);
        } else {
            alert(`${data.message}\n\nThe system will need to be rebooted to enable the Access Point.`);
        }
    })
    .catch(err => {
        alert('Access Point setup request failed. Please try again.');
        console.error('Access Point error:', err);
    })
    .finally(() => {
        document.getElementById('enableAP').disabled = false;
        document.getElementById('enableAP').textContent = 'Enable Access Point';
    });
};

// Image Orientation Controls
const updateImageOrientation = () => {
    const stream = document.getElementById('stream');
    const flipX = document.getElementById('flipX').checked;
    const flipY = document.getElementById('flipY').checked;
    const rotationAngle = document.getElementById('rotationAngle').value;
    
    // Remove existing orientation classes
    stream.classList.remove('flip-x', 'flip-y', 'rotate0', 'rotate90', 'rotate180', 'rotate270');
    
    // Apply flip classes
    if (flipX) stream.classList.add('flip-x');
    if (flipY) stream.classList.add('flip-y');
    
    // Apply rotation class
    stream.classList.add(`rotate${rotationAngle}`);
    
    // Update aspect ratio container to accommodate rotation
    updateStreamAspectRatio();
    
    // Send orientation settings to processing backend
    updateProcessingSettings();
};

// Boundary Box Control
const toggleBoundaryBox = () => {
    const boundaryBox = document.getElementById('boundary-box');
    const showBox = document.getElementById('showBoundaryBox').checked;
    
    if (showBox) {
        boundaryBox.classList.remove('hidden');
        updateBoundaryBox();
    } else {
        boundaryBox.classList.add('hidden');
    }
};

const updateBoundaryBox = () => {
    const stream = document.getElementById('stream');
    const boundaryBox = document.getElementById('boundary-box');
    const roiSize = parseInt(document.getElementById('roiSize').value);
    
    if (!stream.naturalWidth || !stream.naturalHeight) {
        // If image not loaded, try again in a bit
        setTimeout(updateBoundaryBox, 100);
        return;
    }
    
    // Get current orientation settings
    const flipX = document.getElementById('flipX').checked;
    const flipY = document.getElementById('flipY').checked;
    const rotationAngle = parseInt(document.getElementById('rotationAngle').value);
    
    // Calculate the display size of the image
    let displayWidth = stream.offsetWidth;
    let displayHeight = stream.offsetHeight;
    let naturalWidth = stream.naturalWidth;
    let naturalHeight = stream.naturalHeight;
    
    // Account for 90/270 degree rotations that swap dimensions
    if (rotationAngle === 90 || rotationAngle === 270) {
        [naturalWidth, naturalHeight] = [naturalHeight, naturalWidth];
    }
    
    // Calculate scale factors accounting for rotation
    const scaleX = displayWidth / naturalWidth;
    const scaleY = displayHeight / naturalHeight;
    const scale = Math.min(scaleX, scaleY); // Use smaller scale to fit within container
    
    // Calculate square ROI size in display pixels
    const roiDisplaySize = roiSize * scale;
    
    // Center the square ROI (always centered regardless of transformations)
    const left = (displayWidth - roiDisplaySize) / 2;
    const top = (displayHeight - roiDisplaySize) / 2;
    
    // Position the boundary box (square) - transformations are handled by CSS
    boundaryBox.style.left = left + 'px';
    boundaryBox.style.top = top + 'px';
    boundaryBox.style.width = roiDisplaySize + 'px';
    boundaryBox.style.height = roiDisplaySize + 'px';
    
    // Apply the same transformations to the boundary box as the stream
    boundaryBox.classList.remove('flip-x', 'flip-y', 'rotate0', 'rotate90', 'rotate180', 'rotate270');
    if (flipX) boundaryBox.classList.add('flip-x');
    if (flipY) boundaryBox.classList.add('flip-y');
    boundaryBox.classList.add(`rotate${rotationAngle}`);
    
    // Update processing settings to reflect ROI change
    updateProcessingSettings();
};

// Get actual boundary box coordinates for PyScript processing
const getBoundaryBoxCoordinates = () => {
    const stream = document.getElementById('stream');
    const boundaryBox = document.getElementById('boundary-box');
    const roiSize = parseInt(document.getElementById('roiSize').value);
    
    if (!stream.naturalWidth || !stream.naturalHeight || boundaryBox.classList.contains('hidden')) {
        // Return center coordinates as fallback
        return {
            start_x: Math.max(0, (stream.naturalWidth - roiSize) / 2),
            start_y: Math.max(0, (stream.naturalHeight - roiSize) / 2),
            end_x: Math.min(stream.naturalWidth, (stream.naturalWidth + roiSize) / 2),
            end_y: Math.min(stream.naturalHeight, (stream.naturalHeight + roiSize) / 2),
            roi_size: roiSize,
            is_centered: true
        };
    }
    
    // Get current orientation settings
    const flipX = document.getElementById('flipX').checked;
    const flipY = document.getElementById('flipY').checked;
    const rotationAngle = parseInt(document.getElementById('rotationAngle').value);
    
    // Get boundary box display position
    const boxRect = boundaryBox.getBoundingClientRect();
    const streamRect = stream.getBoundingClientRect();
    
    // Calculate relative position within the stream display area
    const relativeX = (boxRect.left - streamRect.left) / streamRect.width;
    const relativeY = (boxRect.top - streamRect.top) / streamRect.height;
    const relativeWidth = boxRect.width / streamRect.width;
    const relativeHeight = boxRect.height / streamRect.height;
    
    // Convert to natural image coordinates
    let naturalWidth = stream.naturalWidth;
    let naturalHeight = stream.naturalHeight;
    
    // Account for rotation that swaps dimensions
    if (rotationAngle === 90 || rotationAngle === 270) {
        [naturalWidth, naturalHeight] = [naturalHeight, naturalWidth];
    }
    
    // Calculate coordinates in natural image space
    let start_x = Math.round(relativeX * naturalWidth);
    let start_y = Math.round(relativeY * naturalHeight);
    let box_width = Math.round(relativeWidth * naturalWidth);
    let box_height = Math.round(relativeHeight * naturalHeight);
    
    // Account for transformations when mapping back to original image coordinates
    if (flipX) {
        start_x = naturalWidth - start_x - box_width;
    }
    if (flipY) {
        start_y = naturalHeight - start_y - box_height;
    }
    
    // Ensure bounds are within image
    start_x = Math.max(0, Math.min(start_x, naturalWidth - box_width));
    start_y = Math.max(0, Math.min(start_y, naturalHeight - box_height));
    
    return {
        start_x: start_x,
        start_y: start_y,
        end_x: start_x + box_width,
        end_y: start_y + box_height,
        roi_size: Math.min(box_width, box_height), // Use smaller dimension for square ROI
        is_centered: false,
        transformations: {
            flip_x: flipX,
            flip_y: flipY,
            rotation: rotationAngle
        }
    };
};

// Make function available globally for PyScript
window.getBoundaryBoxCoordinates = getBoundaryBoxCoordinates;

// Aspect Ratio Management
const updateStreamAspectRatio = () => {
    const stream = document.getElementById('stream');
    
    // Ensure the image maintains its aspect ratio
    stream.style.height = 'auto';
    stream.style.objectFit = 'contain';
    
    // Update boundary box if visible
    if (!document.getElementById('boundary-box').classList.contains('hidden')) {
        setTimeout(updateBoundaryBox, 50); // Small delay to let CSS apply
    }
};

// Slider Controls with +/- buttons
const adjustSlider = (sliderId, delta) => {
    const slider = document.getElementById(sliderId);
    const currentValue = parseFloat(slider.value);
    const step = parseFloat(slider.step);
    const min = parseFloat(slider.min);
    const max = parseFloat(slider.max);
    
    // Calculate new value
    let newValue = currentValue + delta;
    
    // Clamp to min/max bounds
    newValue = Math.max(min, Math.min(max, newValue));
    
    // Round to step precision to avoid floating point errors
    newValue = Math.round(newValue / step) * step;
    
    // Set the new value
    slider.value = newValue;
    
    // Trigger the input event to update displays
    slider.dispatchEvent(new Event('input'));
};

// Processing Settings Update Function
const updateProcessingSettings = () => {
    // Get current settings
    const flipX = document.getElementById('flipX').checked;
    const flipY = document.getElementById('flipY').checked;
    const rotationAngle = parseInt(document.getElementById('rotationAngle').value);
    const roiSize = parseInt(document.getElementById('roiSize').value);
    const colorChannel = document.getElementById('colorChannel').value;
    
    const settings = {
        orientation: {
            flipX: flipX,
            flipY: flipY, 
            rotation: rotationAngle
        },
        roi: {
            size: roiSize,
            centerX: 0.5, // Always center for now
            centerY: 0.5
        },
        processing: {
            colorChannel: colorChannel
        }
    };
    
    console.log('Updating processing settings:', settings);
    
    // Apply transformations to processed canvas
    applyProcessedCanvasTransformations(settings.orientation);
    
    // Update hologram processing if available
    if (typeof window.updateHologramProcessingSettings === 'function') {
        window.updateHologramProcessingSettings(settings);
    }
    
    // Send to backend (if available)
    api('/processing/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(settings)
    }).then(r => r.json()).then(data => {
        console.log('Processing settings updated:', data);
    }).catch(err => {
        console.warn('Could not update backend processing settings (offline mode):', err);
    });
};

// Apply transformations to processed canvas
const applyProcessedCanvasTransformations = (orientation) => {
    const processedCanvas = document.getElementById('processed');
    
    // Remove existing orientation classes
    processedCanvas.classList.remove('flip-x', 'flip-y', 'rotate0', 'rotate90', 'rotate180', 'rotate270');
    
    // Apply flip classes
    if (orientation.flipX) processedCanvas.classList.add('flip-x');
    if (orientation.flipY) processedCanvas.classList.add('flip-y');
    
    // Apply rotation class
    processedCanvas.classList.add(`rotate${orientation.rotation}`);
    
    console.log('Applied transformations to processed canvas:', orientation);
};

// Make the settings update function available globally for PyScript
window.updateHologramProcessingSettings = (settings) => {
    // Store settings globally for hologram processing
    window.hologramSettings = settings;
    console.log('Hologram processing settings updated:', settings);
};

// Initialize processed canvas
const initializeProcessedCanvas = () => {
    const processedCanvas = document.getElementById('processed');
    
    // Ensure the canvas starts square
    const size = Math.min(processedCanvas.width, processedCanvas.height);
    processedCanvas.width = size;
    processedCanvas.height = size;
    
    console.log(`Initialized processed canvas to ${size}x${size}`);
};