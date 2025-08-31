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
    
    // If we're accessing via specific host, use current host with port 8000
    if (currentHost !== '127.0.0.1') {
        detectedUrl = `https://${currentHost}:8000`;
    } else {
        // Default fallback for local development
        detectedUrl = 'https://192.168.4.1:8000';
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

const api = (path, opt = {}) => fetch(baseUrl + path, opt);

const startStream = () => {
    const stream = document.getElementById('stream');
    stream.src = baseUrl + '/stream';
    
    stream.onload = () => {
        updateStreamAspectRatio();
        if (!document.getElementById('boundary-box').classList.contains('hidden')) {
            updateBoundaryBox();
        }
        document.getElementById('status').textContent = 'Stream started';
    };
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (!document.getElementById('boundary-box').classList.contains('hidden')) {
            updateBoundaryBox();
        }
    });
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
                    <div class="border-bottom py-2 network-item" 
                         style="cursor: pointer;" 
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