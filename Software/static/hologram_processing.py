import numpy as np
from js import document, console, ImageData, Uint8ClampedArray, setInterval, clearInterval
from pyodide.ffi import to_js
import asyncio

# Global variables
processing_enabled = False
processing_interval = None
current_wavelength = 440e-9  # nm to m
current_pixelsize = 1.4e-6   # µm to m  
current_dz = 0.005           # mm to m
debug_mode = True            # Enable detailed debugging

console.log("🔧 Starting PyScript hologram processing setup...")

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

def apply_image_transformations(image, flip_x=False, flip_y=False, rotation=0):
    """Apply flip and rotation transformations to image"""
    if flip_x:
        image = np.fliplr(image)
    if flip_y:
        image = np.flipud(image)
    
    # Apply rotation (counter-clockwise)
    if rotation == 90:
        image = np.rot90(image, k=1)
    elif rotation == 180:
        image = np.rot90(image, k=2)
    elif rotation == 270:
        image = np.rot90(image, k=3)
    
    return image

def process_image_for_hologram(width=256, height=256):
    """Process image data through Fresnel propagation using direct canvas access"""
    try:
        if debug_mode:
            console.log(f"Debug: Starting hologram processing with size {width}x{height}")
        
        # Try to get image from camera stream canvas
        stream_canvas = document.getElementById('stream')
        
        if stream_canvas and hasattr(stream_canvas, 'getContext'):
            # Create temporary canvas to get image data
            temp_canvas = document.createElement('canvas')
            temp_ctx = temp_canvas.getContext('2d')
            
            # Set canvas size
            temp_canvas.width = width
            temp_canvas.height = height
            
            # Draw from stream canvas or create test pattern
            try:
                temp_ctx.drawImage(stream_canvas, 0, 0, width, height)
                image_data = temp_ctx.getImageData(0, 0, width, height)
                
                if debug_mode:
                    console.log("Debug: Got image data from camera stream")
                    
            except Exception as e:
                if debug_mode:
                    console.log(f"Debug: Failed to get camera image, creating test pattern: {e}")
                
                # Create synthetic test pattern (interference-like)
                test_img = np.zeros((height, width, 4), dtype=np.uint8)
                
                # Create interference pattern for testing
                y, x = np.mgrid[0:height, 0:width]
                pattern1 = np.sin(2 * np.pi * x / 20) * np.sin(2 * np.pi * y / 20)
                pattern2 = np.sin(2 * np.pi * x / 15 + np.pi/4) * np.sin(2 * np.pi * y / 15 + np.pi/4)
                interference = (pattern1 + pattern2 + 2) / 4 * 255
                
                test_img[:, :, 0] = interference.astype(np.uint8)
                test_img[:, :, 1] = interference.astype(np.uint8)
                test_img[:, :, 2] = interference.astype(np.uint8)
                test_img[:, :, 3] = 255
                
                # Convert to image data
                js_array = to_js(test_img.flatten().tolist())
                image_data = temp_ctx.createImageData(width, height)
                image_data.data.set(js_array)
        
        else:
            if debug_mode:
                console.log("Debug: No stream canvas found, creating test pattern")
            
            # Create synthetic test pattern if no canvas
            test_img = np.zeros((height, width, 4), dtype=np.uint8)
            
            # Create interference pattern for testing
            y, x = np.mgrid[0:height, 0:width]
            pattern1 = np.sin(2 * np.pi * x / 20) * np.sin(2 * np.pi * y / 20)
            pattern2 = np.sin(2 * np.pi * x / 15 + np.pi/4) * np.sin(2 * np.pi * y / 15 + np.pi/4)
            interference = (pattern1 + pattern2 + 2) / 4 * 255
            
            test_img[:, :, 0] = interference.astype(np.uint8)
            test_img[:, :, 1] = interference.astype(np.uint8)
            test_img[:, :, 2] = interference.astype(np.uint8)
            test_img[:, :, 3] = 255
            
            # Convert to image data
            js_array = to_js(test_img.flatten().tolist())
            temp_canvas = document.createElement('canvas')
            temp_ctx = temp_canvas.getContext('2d')
            temp_canvas.width = width
            temp_canvas.height = height
            image_data = temp_ctx.createImageData(width, height)
            image_data.data.set(js_array)
        
        # Convert image data to numpy array
        img_array = np.array(image_data.data).reshape((height, width, 4))
        
        if debug_mode:
            console.log(f"Debug: Image array shape: {img_array.shape}")
        
        # Get settings from the interface
        flip_x = False
        flip_y = False
        rotation = 0
        roi_size = min(256, min(height, width))
        color_channel = 'green'  # default
        
        # Try to get settings from the interface elements
        try:
            flip_x_elem = document.getElementById('flipX')
            if flip_x_elem:
                flip_x = flip_x_elem.checked
                
            flip_y_elem = document.getElementById('flipY')
            if flip_y_elem:
                flip_y = flip_y_elem.checked
                
            rotation_elem = document.getElementById('rotationAngle')
            if rotation_elem:
                rotation = int(rotation_elem.value)
                
            roi_elem = document.getElementById('roiSize')
            if roi_elem:
                roi_size = int(roi_elem.value)
                
            channel_elem = document.getElementById('colorChannel')
            if channel_elem:
                color_channel = channel_elem.value
                
        except Exception as e:
            if debug_mode:
                console.log(f"Debug: Could not read settings from interface: {e}")
        
        if debug_mode:
            console.log(f"Debug: Settings - flipX: {flip_x}, flipY: {flip_y}, rotation: {rotation}, ROI: {roi_size}, channel: {color_channel}")
        
        # Extract color channel
        if color_channel == 'red':
            gray = img_array[:, :, 0].astype(float) / 255.0
        elif color_channel == 'blue':
            gray = img_array[:, :, 2].astype(float) / 255.0
        else:  # green or default
            gray = img_array[:, :, 1].astype(float) / 255.0
        
        # Apply transformations to the full image first
        transformed = apply_image_transformations(gray, flip_x, flip_y, rotation)
        
        if debug_mode:
            console.log(f"Debug: Transformed shape: {transformed.shape}")
        
        # Extract square ROI from center after transformations
        t_height, t_width = transformed.shape
        start_y = max(0, (t_height - roi_size) // 2)
        start_x = max(0, (t_width - roi_size) // 2)
        end_y = min(t_height, start_y + roi_size)
        end_x = min(t_width, start_x + roi_size)
        
        cropped = transformed[start_y:end_y, start_x:end_x]
        
        if debug_mode:
            console.log(f"Debug: Cropped ROI shape: {cropped.shape}")
        
        # Estimate amplitude from intensity (assume sqrt relationship)
        amplitude = np.sqrt(np.abs(cropped))
        
        # Apply Fresnel propagation
        propagated = fresnel_propagator(amplitude, current_pixelsize, current_wavelength, current_dz)
        
        # Calculate intensity
        intensity = abssqr(propagated)
        
        # Normalize for display
        if np.max(intensity) > np.min(intensity):
            intensity = (intensity - np.min(intensity)) / (np.max(intensity) - np.min(intensity))
        intensity = (intensity * 255).astype(np.uint8)
        
        if debug_mode:
            console.log(f"Debug: Final intensity shape: {intensity.shape}")
        
        # Create RGBA output - ensure it's square
        output_size = intensity.shape[0]  # Should already be square from ROI extraction
        result = np.zeros((output_size, output_size, 4), dtype=np.uint8)
        result[:, :, 0] = intensity  # R
        result[:, :, 1] = intensity  # G  
        result[:, :, 2] = intensity  # B
        result[:, :, 3] = 255        # A
        
        # Draw result on processed canvas
        canvas = document.getElementById('processed')
        if canvas:
            ctx = canvas.getContext('2d')
            
            # Convert numpy array to JS format using the working pattern
            js_array = to_js(result.flatten().tolist())
            image_data_result = ctx.createImageData(output_size, output_size)
            image_data_result.data.set(js_array)
            
            # Clear and draw
            ctx.clearRect(0, 0, canvas.width, canvas.height)
            
            # Create temp canvas for the image data
            temp_result_canvas = document.createElement('canvas')
            temp_result_ctx = temp_result_canvas.getContext('2d')
            temp_result_canvas.width = output_size
            temp_result_canvas.height = output_size
            temp_result_ctx.putImageData(image_data_result, 0, 0)
            
            # Scale to fit the display canvas
            ctx.drawImage(temp_result_canvas, 0, 0, canvas.width, canvas.height)
            
            if debug_mode:
                console.log("Debug: Successfully updated processed canvas")
        
        # Update status
        from js import Date
        document.getElementById('last-processed').textContent = Date.new().toLocaleTimeString()
        
        return True
        
    except Exception as e:
        console.log(f"Processing error: {e}")
        if debug_mode:
            console.log(f"Debug: Exception type: {type(e).__name__}")
            import traceback
            console.log(f"Debug: Full traceback: {traceback.format_exc()}")
        return False

def toggle_processing(event=None):
    """Toggle real-time processing on/off"""
    global processing_enabled, processing_interval
    
    processing_enabled = not processing_enabled
    
    if processing_enabled:
        # Start processing every 1 second (not too frequent to avoid overwhelming)
        def process_frame_timer():
            process_image_for_hologram()
        
        processing_interval = setInterval(process_frame_timer, 1000)
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

def process_single_frame(event=None):
    """Process a single frame"""
    process_image_for_hologram()

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
    wavelength_elem = document.getElementById('wavelength')
    if wavelength_elem:
        wavelength_nm = float(wavelength_elem.value)
        current_wavelength = wavelength_nm * 1e-9
        wavelength_value_elem = document.getElementById('wavelength-value')
        if wavelength_value_elem:
            wavelength_value_elem.textContent = str(int(wavelength_nm))
    
    # Update pixel size (µm to m)
    pixelsize_elem = document.getElementById('pixelsize')
    if pixelsize_elem:
        pixelsize_um = float(pixelsize_elem.value)
        current_pixelsize = pixelsize_um * 1e-6
        pixelsize_value_elem = document.getElementById('pixelsize-value')
        if pixelsize_value_elem:
            pixelsize_value_elem.textContent = str(pixelsize_um)
    
    # Update distance (mm to m)
    dz_elem = document.getElementById('dz')
    if dz_elem:
        dz_mm = float(dz_elem.value)
        current_dz = dz_mm * 1e-3
        dz_value_elem = document.getElementById('dz-value')
        if dz_value_elem:
            dz_value_elem.textContent = str(dz_mm)

# Set up event listeners using direct assignment
try:
    toggle_btn = document.getElementById('toggleProcessing')
    if toggle_btn:
        toggle_btn.onclick = toggle_processing
        
    process_btn = document.getElementById('processFrame') 
    if process_btn:
        process_btn.onclick = process_single_frame
        
    debug_btn = document.getElementById('toggleDebug')
    if debug_btn:
        debug_btn.onclick = toggle_debug_mode

    # Parameter slider listeners
    wavelength_slider = document.getElementById('wavelength')
    if wavelength_slider:
        wavelength_slider.oninput = update_parameters
        
    pixelsize_slider = document.getElementById('pixelsize')
    if pixelsize_slider:
        pixelsize_slider.oninput = update_parameters
        
    dz_slider = document.getElementById('dz')
    if dz_slider:
        dz_slider.oninput = update_parameters

    # Initial parameter update
    update_parameters()
    
    console.log("✅ PyScript hologram processing initialized successfully!")
    
    # Test with a single frame to verify everything works
    process_image_for_hologram()
    
except Exception as e:
    console.log(f"❌ Error setting up event listeners: {e}")
    import traceback
    console.log(f"Debug: Traceback: {traceback.format_exc()}")