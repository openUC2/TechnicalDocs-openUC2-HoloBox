// JavaScript for camera controls
let baseUrl = location.origin;

// Image transformation settings
let transformSettings = {
    flipX: false,
    flipY: false,
    rotate90: false
};

// Make baseUrl available globally
window.baseUrl = baseUrl;

// Auto-detect and suggest IP address
function detectAndSetDefaultIP() {
    // Try to get current IP from the browser's hostname
    const hostname = window.location.hostname;
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
        baseUrl = `http://${hostname}:8000`;
    } else {
        // Default to Raspberry Pi AP mode IP
        baseUrl = 'http://192.168.4.1:8000';
    }
    
    document.getElementById('host').value = baseUrl.replace('http://', '').replace('https://', '');
    window.baseUrl = baseUrl;
}

document.addEventListener('DOMContentLoaded', function() {
    // Auto-detect IP on startup
    detectAndSetDefaultIP();
    
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
    
    // Boundary box controls
    document.getElementById('showBoundary').onchange = toggleBoundaryBox;
    document.getElementById('adjustBoundary').onclick = adjustBoundaryBox;
    
    // Image orientation controls
    document.getElementById('flipX').onchange = updateImageTransform;
    document.getElementById('flipY').onchange = updateImageTransform;
    document.getElementById('rotate90').onchange = updateImageTransform;
    
    // Slider event listeners for real-time updates
    setupSliderListeners();
    
    // Initialize
    document.getElementById('status').textContent = 'Ready - Click Start Stream to begin';
    refreshWifiStatus(); // Load initial WiFi status
});

function setupSliderListeners() {
    const sliders = ['wavelength', 'pixelsize', 'dz'];
    sliders.forEach(sliderId => {
        const slider = document.getElementById(sliderId);
        const valueSpan = document.getElementById(sliderId + '-value');
        
        slider.oninput = function() {
            valueSpan.textContent = parseFloat(this.value).toFixed(this.step.includes('.') ? 2 : 0);
        };
    });
}

function adjustSlider(sliderId, delta) {
    const slider = document.getElementById(sliderId);
    const newValue = parseFloat(slider.value) + delta;
    const min = parseFloat(slider.min);
    const max = parseFloat(slider.max);
    
    if (newValue >= min && newValue <= max) {
        slider.value = newValue.toFixed(2);
        const valueSpan = document.getElementById(sliderId + '-value');
        valueSpan.textContent = parseFloat(slider.value).toFixed(slider.step.includes('.') ? 2 : 0);
        
        // Trigger input event for any listening processing code
        slider.dispatchEvent(new Event('input'));
    }
}

function toggleBoundaryBox() {
    const boundaryBox = document.getElementById('boundaryBox');
    const isChecked = document.getElementById('showBoundary').checked;
    boundaryBox.style.display = isChecked ? 'block' : 'none';
}

function adjustBoundaryBox() {
    // Simple boundary box adjustment - could be expanded with drag handles
    const boundaryBox = document.getElementById('boundaryBox');
    const currentTop = parseInt(boundaryBox.style.top) || 20;
    const currentLeft = parseInt(boundaryBox.style.left) || 20;
    
    // Cycle through different preset positions
    if (currentTop === 20 && currentLeft === 20) {
        // Center position
        boundaryBox.style.top = '30%';
        boundaryBox.style.left = '30%';
        boundaryBox.style.width = '40%';
        boundaryBox.style.height = '40%';
    } else if (currentTop === 30) {
        // Smaller center position
        boundaryBox.style.top = '35%';
        boundaryBox.style.left = '35%';
        boundaryBox.style.width = '30%';
        boundaryBox.style.height = '30%';
    } else {
        // Back to default
        boundaryBox.style.top = '20%';
        boundaryBox.style.left = '20%';
        boundaryBox.style.width = '60%';
        boundaryBox.style.height = '60%';
    }
    
    document.getElementById('status').textContent = 'Processing area adjusted';
}

function updateImageTransform() {
    transformSettings.flipX = document.getElementById('flipX').checked;
    transformSettings.flipY = document.getElementById('flipY').checked;
    transformSettings.rotate90 = document.getElementById('rotate90').checked;
    
    const stream = document.getElementById('stream');
    let transform = '';
    
    if (transformSettings.flipX) {
        transform += 'scaleX(-1) ';
    }
    if (transformSettings.flipY) {
        transform += 'scaleY(-1) ';
    }
    if (transformSettings.rotate90) {
        transform += 'rotate(90deg) ';
    }
    
    stream.style.transform = transform.trim();
    
    document.getElementById('status').textContent = 'Image transformation updated';
}

const setHost = () => {
    const val = document.getElementById('host').value.trim();
    if (val) {
        // Add protocol if not present
        if (!val.startsWith('http://') && !val.startsWith('https://')) {
            baseUrl = 'http://' + val;
        } else {
            baseUrl = val.replace(/\/+$/, '');
        }
        window.baseUrl = baseUrl;  // Update global reference
        document.getElementById('status').textContent = `API URL set to ${baseUrl}`;
    }
};

const api = (path, opt = {}) => fetch(baseUrl + path, opt);

const startStream = () => {
    document.getElementById('stream').src = baseUrl + '/stream';
    document.getElementById('status').textContent = 'Stream started - optimized for low latency';
    
    // Apply current transformations to stream
    updateImageTransform();
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