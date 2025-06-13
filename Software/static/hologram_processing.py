import numpy as np
from js import document, console, ImageData, Uint8ClampedArray, setInterval, clearInterval
from pyodide.ffi import create_proxy
import asyncio

# Global variables
processing_enabled = False
processing_interval = None
current_wavelength = 440e-9  # nm to m
current_pixelsize = 1.4e-6   # µm to m  
current_dz = 0.005           # mm to m

def abssqr(x):
    """Calculate intensity (what a detector sees)"""
    return np.real(x * np.conj(x))

def FT(x):
    """Forward Fourier transform with proper frequency shift"""
    return np.fft.fftshift(np.fft.fft2(x))

def iFT(x):
    """Inverse Fourier transform with proper frequency shift"""
    return np.fft.ifft2(np.fft.ifftshift(x))

def fresnel_propagator(E0, ps, lambda0, z):
    """
    Freespace propagation using Fresnel kernel
    
    Args:
        E0: Initial complex field in x-y source plane
        ps: Pixel size in meters
        lambda0: Wavelength in meters
        z: Distance from sensor to object in meters
    
    Returns:
        Ef: Propagated output field
    """
    upsample_scale = 1
    n = upsample_scale * E0.shape[1]  # Image width in pixels
    grid_size = ps * n                # Grid size in x-direction
    
    # Inverse space (frequency domain)
    fx = np.linspace(-(n-1)/2*(1/grid_size), (n-1)/2*(1/grid_size), n)
    fy = np.linspace(-(n-1)/2*(1/grid_size), (n-1)/2*(1/grid_size), n)
    Fx, Fy = np.meshgrid(fx, fy)
    
    # Fresnel kernel / point spread function
    H = np.exp(1j*(2 * np.pi / lambda0) * z) * np.exp(1j * np.pi * lambda0 * z * (Fx**2 + Fy**2))
    
    # Compute FFT
    E0fft = FT(E0)
    
    # Multiply spectrum with Fresnel phase factor
    G = H * E0fft
    Ef = iFT(G)  # Output after inverse FFT
    
    return Ef

def process_image_data(image_data, width, height):
    """Process image data through Fresnel propagation"""
    try:
        # Convert image data to numpy array
        # ImageData is in RGBA format
        img_array = np.array(image_data).reshape((height, width, 4))
        
        # Convert to grayscale and normalize
        gray = img_array[:, :, 0] * 0.299 + img_array[:, :, 1] * 0.587 + img_array[:, :, 2] * 0.114
        gray = gray / 255.0
        
        # Crop to smaller size for faster processing (power of 2)
        crop_size = min(256, min(height, width))
        start_y = (height - crop_size) // 2
        start_x = (width - crop_size) // 2
        cropped = gray[start_y:start_y + crop_size, start_x:start_x + crop_size]
        
        # Estimate amplitude from intensity
        amplitude = np.sqrt(cropped)
        
        # Apply Fresnel propagation
        propagated = fresnel_propagator(amplitude, current_pixelsize, current_wavelength, current_dz)
        
        # Calculate intensity
        intensity = abssqr(propagated)
        
        # Normalize for display
        intensity = (intensity - np.min(intensity)) / (np.max(intensity) - np.min(intensity))
        intensity = (intensity * 255).astype(np.uint8)
        
        # Resize back to original canvas size
        if crop_size != width or crop_size != height:
            # Simple repeat for upsampling (can be improved with proper interpolation)
            scale_x = width // crop_size
            scale_y = height // crop_size
            intensity = np.repeat(np.repeat(intensity, scale_y, axis=0), scale_x, axis=1)
            
            # Ensure exact size match
            intensity = intensity[:height, :width]
        
        # Convert back to RGBA
        result = np.zeros((height, width, 4), dtype=np.uint8)
        result[:, :, 0] = intensity  # R
        result[:, :, 1] = intensity  # G  
        result[:, :, 2] = intensity  # B
        result[:, :, 3] = 255        # A
        
        return result.flatten()
        
    except Exception as e:
        console.log(f"Processing error: {e}")
        return None

def process_frame_from_snapshot():
    """Process frame using snapshot API to avoid cross-origin issues"""
    try:
        from js import fetch, location
        from pyodide.ffi import to_js
        
        # Use the JavaScript API to fetch a snapshot
        # This avoids the cross-origin canvas issue
        def process_snapshot(image_blob):
            # Create a new image element
            img = document.createElement('img')
            
            def on_image_load(event):
                try:
                    # Create a temporary canvas to process the image
                    temp_canvas = document.createElement('canvas')
                    temp_ctx = temp_canvas.getContext('2d')
                    
                    # Set canvas size to match image
                    temp_canvas.width = img.naturalWidth
                    temp_canvas.height = img.naturalHeight
                    
                    # Draw image to temporary canvas
                    temp_ctx.drawImage(img, 0, 0)
                    
                    # Get image data
                    image_data = temp_ctx.getImageData(0, 0, temp_canvas.width, temp_canvas.height)
                    
                    # Process the image
                    processed_data = process_image_data(image_data.data, temp_canvas.width, temp_canvas.height)
                    
                    if processed_data is not None:
                        # Display on the main canvas
                        canvas = document.getElementById('processed')
                        ctx = canvas.getContext('2d')
                        
                        # Create new image data and display
                        new_image_data = ImageData.new(Uint8ClampedArray.new(processed_data), temp_canvas.width, temp_canvas.height)
                        
                        # Scale to fit canvas
                        ctx.clearRect(0, 0, canvas.width, canvas.height)
                        temp_canvas2 = document.createElement('canvas')
                        temp_ctx2 = temp_canvas2.getContext('2d')
                        temp_canvas2.width = temp_canvas.width
                        temp_canvas2.height = temp_canvas.height
                        temp_ctx2.putImageData(new_image_data, 0, 0)
                        
                        # Scale and draw to main canvas
                        ctx.drawImage(temp_canvas2, 0, 0, canvas.width, canvas.height)
                        
                        # Update status with current time from JS Date object
                        from js import Date
                        document.getElementById('last-processed').textContent = Date.new().toLocaleTimeString()
                    
                    # Clean up
                    from js import URL
                    URL.revokeObjectURL(img.src)
                    
                except Exception as e:
                    console.log(f"Snapshot processing error: {e}")
            
            img.onload = create_proxy(on_image_load)
            from js import URL
            img.src = URL.createObjectURL(image_blob)
        
        # Fetch snapshot from API
        from js import window
        base_url = window.baseUrl if hasattr(window, 'baseUrl') else location.origin
        
        def handle_response(response):
            response.blob().then(create_proxy(process_snapshot))
        
        def handle_error(error):
            console.log(f"Failed to fetch snapshot: {error}")
        
        fetch(f"{base_url}/snapshot").then(create_proxy(handle_response)).catch(create_proxy(handle_error))
        
    except Exception as e:
        console.log(f"Process frame error: {e}")

def update_processed_canvas(event=None):
    """Update the processed canvas with Fresnel propagation using snapshot API"""
    process_frame_from_snapshot()

def toggle_processing(event=None):  # Fixed: added event parameter
    """Toggle real-time processing on/off"""
    global processing_enabled, processing_interval
    
    processing_enabled = not processing_enabled
    
    if processing_enabled:
        # Start processing every 500ms (slower to avoid overwhelming the API)
        processing_interval = setInterval(create_proxy(update_processed_canvas), 500)
        document.getElementById('toggleProcessing').textContent = 'Disable Processing'
        document.getElementById('processing-enabled').textContent = 'Enabled'
        document.getElementById('status').textContent = 'Processing frames...'
    else:
        # Stop processing
        if processing_interval:
            clearInterval(processing_interval)
        document.getElementById('toggleProcessing').textContent = 'Enable Processing'
        document.getElementById('processing-enabled').textContent = 'Disabled'
        document.getElementById('status').textContent = 'Processing stopped'

def update_parameters(event=None):
    """Update processing parameters from sliders"""
    global current_wavelength, current_pixelsize, current_dz
    
    # Update wavelength (nm to m)
    wavelength_nm = float(document.getElementById('wavelength').value)
    current_wavelength = wavelength_nm * 1e-9
    document.getElementById('wavelength-value').textContent = str(int(wavelength_nm))
    
    # Update pixel size (µm to m)
    pixelsize_um = float(document.getElementById('pixelsize').value)
    current_pixelsize = pixelsize_um * 1e-6
    document.getElementById('pixelsize-value').textContent = str(pixelsize_um)
    
    # Update distance (mm to m)
    dz_mm = float(document.getElementById('dz').value)
    current_dz = dz_mm * 1e-3
    document.getElementById('dz-value').textContent = str(dz_mm)

# Set up event listeners
document.getElementById('toggleProcessing').onclick = create_proxy(toggle_processing)
document.getElementById('processFrame').onclick = create_proxy(update_processed_canvas)

# Parameter slider listeners
document.getElementById('wavelength').oninput = create_proxy(update_parameters)
document.getElementById('pixelsize').oninput = create_proxy(update_parameters)
document.getElementById('dz').oninput = create_proxy(update_parameters)

# Initial parameter update
update_parameters()

console.log("PyScript hologram processing initialized")