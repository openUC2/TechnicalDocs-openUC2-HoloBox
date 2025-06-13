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
debug_mode = True            # Enable detailed debugging

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
        if debug_mode:
            console.log(f"Debug: Starting process_image_data with width={width}, height={height}")
        
        # Convert image data to numpy array
        # ImageData is in RGBA format
        img_array = np.array(image_data).reshape((height, width, 4))
        
        if debug_mode:
            console.log(f"Debug: Image array shape: {img_array.shape}")
        
        # Convert to grayscale and normalize
        gray = img_array[:, :, 0] * 0.299 + img_array[:, :, 1] * 0.587 + img_array[:, :, 2] * 0.114
        gray = gray / 255.0
        
        if debug_mode:
            console.log(f"Debug: Grayscale shape: {gray.shape}")
        
        # Crop to smaller size for faster processing (power of 2)
        crop_size = min(256, min(height, width))
        start_y = (height - crop_size) // 2
        start_x = (width - crop_size) // 2
        cropped = gray[start_y:start_y + crop_size, start_x:start_x + crop_size]
        
        if debug_mode:
            console.log(f"Debug: Crop size: {crop_size}, cropped shape: {cropped.shape}")
        
        # Estimate amplitude from intensity
        amplitude = np.sqrt(cropped)
        
        if debug_mode:
            console.log(f"Debug: Amplitude shape: {amplitude.shape}")
        
        # Apply Fresnel propagation
        propagated = fresnel_propagator(amplitude, current_pixelsize, current_wavelength, current_dz)
        
        if debug_mode:
            console.log(f"Debug: Propagated shape: {propagated.shape}")
        
        # Calculate intensity
        intensity = abssqr(propagated)
        
        if debug_mode:
            console.log(f"Debug: Intensity shape: {intensity.shape}")
        
        # Normalize for display
        intensity = (intensity - np.min(intensity)) / (np.max(intensity) - np.min(intensity))
        intensity = (intensity * 255).astype(np.uint8)
        
        if debug_mode:
            console.log(f"Debug: Normalized intensity shape: {intensity.shape}")
        
        # Resize back to original canvas size using proper interpolation
        if intensity.shape[0] != height or intensity.shape[1] != width:
            if debug_mode:
                console.log(f"Debug: Resizing from {intensity.shape} to ({height}, {width})")
            
            # Use a simple but robust interpolation approach
            # Calculate scaling factors
            scale_y = height / intensity.shape[0]
            scale_x = width / intensity.shape[1]
            
            if debug_mode:
                console.log(f"Debug: Scale factors - y: {scale_y}, x: {scale_x}")
            
            # Create coordinate grids for interpolation
            y_old = np.arange(intensity.shape[0])
            x_old = np.arange(intensity.shape[1])
            y_new = np.linspace(0, intensity.shape[0] - 1, height)
            x_new = np.linspace(0, intensity.shape[1] - 1, width)
            
            # Simple nearest neighbor interpolation
            y_indices = np.round(y_new).astype(int)
            x_indices = np.round(x_new).astype(int)
            
            # Ensure indices are within bounds
            y_indices = np.clip(y_indices, 0, intensity.shape[0] - 1)
            x_indices = np.clip(x_indices, 0, intensity.shape[1] - 1)
            
            # Create meshgrid and resize
            Y, X = np.meshgrid(y_indices, x_indices, indexing='ij')
            intensity = intensity[Y, X]
            
            if debug_mode:
                console.log(f"Debug: Resized intensity shape: {intensity.shape}")
        
        # Convert back to RGBA
        result = np.zeros((height, width, 4), dtype=np.uint8)
        result[:, :, 0] = intensity  # R
        result[:, :, 1] = intensity  # G  
        result[:, :, 2] = intensity  # B
        result[:, :, 3] = 255        # A
        
        if debug_mode:
            console.log(f"Debug: Final result shape: {result.shape}")
        
        return result.flatten()
        
    except Exception as e:
        console.log(f"Processing error: {e}")
        if debug_mode:
            console.log(f"Debug: Exception type: {type(e).__name__}")
            # Try to get more detailed error information
            import traceback
            console.log(f"Debug: Full traceback: {traceback.format_exc()}")
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

def toggle_debug_mode(event=None):
    """Toggle debug mode on/off"""
    global debug_mode
    
    debug_mode = not debug_mode
    
    if debug_mode:
        document.getElementById('toggleDebug').textContent = 'Disable Debug'
        document.getElementById('debug-status').textContent = 'Enabled'
        console.log("Debug mode enabled - detailed logging active")
    else:
        document.getElementById('toggleDebug').textContent = 'Enable Debug'
        document.getElementById('debug-status').textContent = 'Disabled'
        console.log("Debug mode disabled")

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
document.getElementById('toggleDebug').onclick = create_proxy(toggle_debug_mode)

# Parameter slider listeners
document.getElementById('wavelength').oninput = create_proxy(update_parameters)
document.getElementById('pixelsize').oninput = create_proxy(update_parameters)
document.getElementById('dz').oninput = create_proxy(update_parameters)

# Initial parameter update
update_parameters()

console.log("PyScript hologram processing initialized")