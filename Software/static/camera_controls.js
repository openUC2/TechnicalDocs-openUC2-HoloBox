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
    
    // Initialize
    document.getElementById('status').textContent = 'Ready - Click Start Stream to begin';
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