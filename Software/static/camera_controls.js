// JavaScript for camera controls
let baseUrl = location.origin;

// Make baseUrl available globally for PyScript
window.baseUrl = baseUrl;

document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners once DOM is loaded
    document.getElementById('setHost').onclick = setHost;
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
    document.getElementById('rotate90').onchange = updateImageOrientation;
    
    // Boundary box control
    document.getElementById('showBoundaryBox').onchange = toggleBoundaryBox;
    
    // Initialize default IP and auto-suggest current device IP
    initializeHostSuggestion();
    
    // Initialize
    document.getElementById('status').textContent = 'Ready - Click Start Stream to begin';
    refreshWifiStatus(); // Load initial WiFi status
});

// Auto-suggest current device IP or use default
const initializeHostSuggestion = () => {
    const hostInput = document.getElementById('host');
    
    // If already has a value (from HTML), use it as default
    if (hostInput.value && hostInput.value.trim()) {
        baseUrl = hostInput.value.trim().replace(/\/+$/, '');
        window.baseUrl = baseUrl;
        return;
    }
    
    // Try to detect current IP for better suggestion
    const currentHost = window.location.hostname;
    const currentPort = window.location.port;
    const protocol = window.location.protocol;
    
    let suggestedUrl = 'http://192.168.4.1:8000'; // Default fallback
    
    // If we're not on localhost, suggest current host with port 8000
    if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
        if (currentPort && currentPort !== '80' && currentPort !== '443') {
            suggestedUrl = `${protocol}//${currentHost}:8000`;
        } else {
            suggestedUrl = `${protocol}//${currentHost}:8000`;
        }
    }
    
    hostInput.value = suggestedUrl;
    baseUrl = suggestedUrl.replace(/\/+$/, '');
    window.baseUrl = baseUrl;
};

const setHost = () => {
    const val = document.getElementById('host').value.trim();
    if (val) {
        baseUrl = val.replace(/\/+$/, '');
        window.baseUrl = baseUrl;  // Update global reference
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
    const rotate90 = document.getElementById('rotate90').checked;
    
    // Remove existing orientation classes
    stream.classList.remove('flip-x', 'flip-y', 'rotate90');
    
    // Apply new orientation classes
    if (flipX) stream.classList.add('flip-x');
    if (flipY) stream.classList.add('flip-y');
    if (rotate90) stream.classList.add('rotate90');
    
    // Update aspect ratio container to accommodate rotation
    updateStreamAspectRatio();
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
    
    if (!stream.naturalWidth || !stream.naturalHeight) {
        // If image not loaded, try again in a bit
        setTimeout(updateBoundaryBox, 100);
        return;
    }
    
    // Calculate the display size of the image
    const displayWidth = stream.offsetWidth;
    const displayHeight = stream.offsetHeight;
    
    // Define the processing region (e.g., center 80% of the image)
    const regionWidth = displayWidth * 0.8;
    const regionHeight = displayHeight * 0.8;
    const left = (displayWidth - regionWidth) / 2;
    const top = (displayHeight - regionHeight) / 2;
    
    // Position the boundary box
    boundaryBox.style.left = left + 'px';
    boundaryBox.style.top = top + 'px';
    boundaryBox.style.width = regionWidth + 'px';
    boundaryBox.style.height = regionHeight + 'px';
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