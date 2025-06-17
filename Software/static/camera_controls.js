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
    
    // Initialize
    document.getElementById('status').textContent = 'Ready - Click Start Stream to begin';
    refreshWifiStatus(); // Load initial WiFi status
});

const setHost = () => {
    const val = document.getElementById('host').value.trim();
    if (val) {
        baseUrl = val.replace(/\/+$/, '');
        window.baseUrl = baseUrl;  // Update global reference
    }
};

const api = (path, opt = {}) => fetch(baseUrl + path, opt);

const startStream = () => {
    document.getElementById('stream').src = baseUrl + '/stream';
    document.getElementById('status').textContent = 'Stream started';
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