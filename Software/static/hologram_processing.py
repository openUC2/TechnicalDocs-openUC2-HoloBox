import numpy as np
from js import document, console, ImageData, Uint8ClampedArray, setInterval, clearInterval
from pyodide.ffi import to_js, create_proxy
import asyncio

# Global variables
processing_enabled = False
processing_interval = None
timer_proxy = None  # Keep reference to prevent garbage collection
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

def get_roi_coordinates_from_boundary_box(img_width, img_height, roi_size, flip_x, flip_y, rotation):
    """
    Calculate the actual pixel coordinates of the ROI based on the boundary box position.
    This function uses the JavaScript boundary box coordinates to get the exact region.
    
    Args:
        img_width: Width of the source image
        img_height: Height of the source image  
        roi_size: Size of the square ROI in pixels
        flip_x: Whether image is flipped horizontally
        flip_y: Whether image is flipped vertically
        rotation: Rotation angle (0, 90, 180, 270)
    
    Returns:
        Dictionary with start_x, start_y, end_x, end_y coordinates
    """
    try:
        # Use JavaScript function to get actual boundary box coordinates
        from js import window
        if hasattr(window, 'getBoundaryBoxCoordinates'):
            bbox_coords = window.getBoundaryBoxCoordinates()
            
            # Convert from JavaScript object to Python dict-like access
            start_x = int(bbox_coords.start_x or 0)
            start_y = int(bbox_coords.start_y or 0)  
            end_x = int(bbox_coords.end_x or img_width)
            end_y = int(bbox_coords.end_y or img_height)
            
            # Scale coordinates to match our processing canvas size
            # The JavaScript gives us natural image coordinates, we need processing canvas coordinates
            stream_img = document.getElementById('stream')
            if stream_img and stream_img.naturalWidth > 0:
                scale_x = img_width / stream_img.naturalWidth
                scale_y = img_height / stream_img.naturalHeight
                
                start_x = int(start_x * scale_x)
                start_y = int(start_y * scale_y)
                end_x = int(end_x * scale_x)
                end_y = int(end_y * scale_y)
            
            # Ensure bounds are within our processing canvas
            start_x = max(0, min(start_x, img_width))
            start_y = max(0, min(start_y, img_height))
            end_x = max(start_x + 1, min(end_x, img_width))
            end_y = max(start_y + 1, min(end_y, img_height))
            
            if debug_mode:
                console.log(f"Debug: Using boundary box coordinates - start: ({start_x}, {start_y}), end: ({end_x}, {end_y})")
            
            return {
                'start_x': start_x,
                'start_y': start_y,
                'end_x': end_x,
                'end_y': end_y,
                'width': end_x - start_x,
                'height': end_y - start_y
            }
        else:
            if debug_mode:
                console.log("Debug: getBoundaryBoxCoordinates not available, using fallback")
    
    except Exception as e:
        if debug_mode:
            console.log(f"Debug: Error getting boundary box coordinates: {e}")
    
    # Fallback to center crop when boundary box is not available or hidden
    center_x = img_width // 2
    center_y = img_height // 2
    start_x = max(0, center_x - roi_size // 2)
    start_y = max(0, center_y - roi_size // 2)
    end_x = min(img_width, start_x + roi_size)
    end_y = min(img_height, start_y + roi_size)
    
    if debug_mode:
        console.log(f"Debug: Using fallback center crop - start: ({start_x}, {start_y}), end: ({end_x}, {end_y})")
    
    return {
        'start_x': start_x,
        'start_y': start_y,
        'end_x': end_x,
        'end_y': end_y,
        'width': end_x - start_x,
        'height': end_y - start_y
    }

def process_image_for_hologram(width=256, height=256):
    """Process image data through Fresnel propagation using stream image"""
    try:
        if debug_mode:
            console.log(f"Debug: Starting hologram processing with size {width}x{height}")
        
        # Try to get image from camera stream (img element)
        stream_img = document.getElementById('stream')
        
        # Create temporary canvas to process the image
        temp_canvas = document.createElement('canvas')
        temp_ctx = temp_canvas.getContext('2d')
        temp_canvas.width = width
        temp_canvas.height = height
        
        # Try to draw from stream image
        image_data = None
        
        if debug_mode:
            if stream_img:
                console.log(f"Debug: Stream img found - src: {stream_img.src}")
                console.log(f"Debug: Stream img dimensions: {stream_img.width}x{stream_img.height}")
                console.log(f"Debug: Stream img complete: {stream_img.complete}")
            else:
                console.log("Debug: Stream img element not found")
        
        try:
            if (stream_img and hasattr(stream_img, 'src') and 
                stream_img.src and not stream_img.src.startswith('data:,') and
                stream_img.complete and stream_img.width > 0):
                # Draw the stream image to canvas
                temp_ctx.drawImage(stream_img, 0, 0, width, height)
                image_data = temp_ctx.getImageData(0, 0, width, height)
                
                if debug_mode:
                    console.log("Debug: Successfully got image data from camera stream")
            else:
                if debug_mode:
                    console.log("Debug: Stream image not ready or invalid")
                raise Exception("Stream not ready")
                
        except Exception as e:
            if debug_mode:
                console.log(f"Debug: Failed to get camera image, creating test pattern: {e}")
            
            # Create synthetic test pattern
            test_img = np.zeros((height, width, 4), dtype=np.uint8)
            
            # Create interference pattern for testing
            y, x = np.mgrid[0:height, 0:width]
            pattern1 = np.sin(2 * np.pi * x / 20) * np.sin(2 * np.pi * y / 20)
            pattern2 = np.sin(2 * np.pi * x / 15 + np.pi/4) * np.sin(2 * np.pi * y / 15 + np.pi/4)
            interference = (pattern1 + pattern2 + 2) / 4 * 255
            
            test_img[:, :, 0] = interference.astype(np.uint8)
            test_img[:, :, 1] = interference.astype(np.uint8)  
            test_img[:, :, 2] = interference.astype(np.uint8)
            test_img[:, :, 3] = 255  # Alpha channel
            
            # Convert to JavaScript array and create ImageData
            js_array = to_js(test_img.flatten().tolist())
            clamped_array = Uint8ClampedArray.new(js_array)
            image_data = ImageData.new(clamped_array, width, height)
            temp_canvas = document.createElement('canvas')
            temp_ctx = temp_canvas.getContext('2d')
            temp_canvas.width = width
            temp_canvas.height = height
            image_data = temp_ctx.createImageData(width, height)
            image_data.data.set(js_array)
        
        # Convert image data to numpy array
        if debug_mode:
            console.log(f"Debug: Converting image data to numpy array to height: {stream_img.height}, width: {stream_img.width}")

        img_array = np.array(image_data.data).reshape((stream_img.width, stream_img.height, 3))

        if debug_mode:
            console.log(f"Debug: Image array shape: {img_array.shape}")
        
        # Get settings from the interface
        flip_x = False
        flip_y = False
        rotation = 0
        roi_size = min(height, width)
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
        
        # Get ROI coordinates from boundary box instead of centering
        # roi_coords = get_roi_coordinates_from_boundary_box(width, height, roi_size, flip_x, flip_y, rotation)
        # TODO: We can assume that we crop a central region of NxN pixels
        roi_coords = {}
        roi_coords['start_x'] = (width - roi_size) // 2
        roi_coords['start_y'] = (height - roi_size) // 2
        roi_coords['end_x'] = roi_coords['start_x'] + roi_size
        roi_coords['end_y'] = roi_coords['start_y'] + roi_size

        if debug_mode:
            console.log(f"Debug: ROI coordinates - start_x: {roi_coords['start_x']}, start_y: {roi_coords['start_y']}, end_x: {roi_coords['end_x']}, end_y: {roi_coords['end_y']}")

        # Ensure the image is at least as large as the ROI in both directions by padding
        if gray.shape[0] < roi_size or gray.shape[1] < roi_size:
            console.log("Warning: Image is smaller than ROI, padding with zeros")
            padded = np.zeros((roi_size, roi_size), dtype=np.float32)
            start_y = (roi_size - gray.shape[0]) // 2
            start_x = (roi_size - gray.shape[1]) // 2
            padded[start_y:start_y + gray.shape[0], start_x:start_x + gray.shape[1]] = gray
            gray = padded

        # Extract the ROI region directly from the original image (before transformations)
        # This way we get the exact region that the user selected with the red box
        cropped = gray[roi_coords['start_y']:roi_coords['end_y'], roi_coords['start_x']:roi_coords['end_x']]
        
        # Now apply transformations only to the cropped ROI
        if cropped.shape[0] > 0 and cropped.shape[1] > 0:
            cropped = apply_image_transformations(cropped, flip_x, flip_y, rotation)
        
        
        if debug_mode:
            console.log(f"Debug: Final cropped ROI shape: {cropped.shape}")
        
        # Validate that we have a proper ROI
        if cropped.shape[0] == 0 or cropped.shape[1] == 0:
            console.log("Warning: Empty ROI, falling back to center crop")
            # Fallback to center crop
            center_y, center_x = gray.shape[0] // 2, gray.shape[1] // 2
            half_roi = roi_size // 2
            start_y = max(0, center_y - half_roi)
            start_x = max(0, center_x - half_roi)
            end_y = min(gray.shape[0], start_y + roi_size)
            end_x = min(gray.shape[1], start_x + roi_size)
            cropped = gray[start_y:end_y, start_x:end_x]
            cropped = apply_image_transformations(cropped, flip_x, flip_y, rotation)
        
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
    """Toggle hologram processing on/off"""
    global processing_enabled, processing_interval, timer_proxy
    
    processing_enabled = not processing_enabled
    
    if processing_enabled:
        # Start processing every 1 second (not too frequent to avoid overwhelming)
        def process_frame_timer():
            try:
                process_image_for_hologram()
            except Exception as e:
                console.log(f"❌ Error in timer callback: {e}")
        
        # Create a proper proxy for the JavaScript callback and keep reference
        timer_proxy = create_proxy(process_frame_timer)
        processing_interval = setInterval(timer_proxy, 1000)
        document.getElementById('toggleProcessing').textContent = 'Disable Processing'
        document.getElementById('processing-enabled').textContent = 'Enabled'
        document.getElementById('status').textContent = 'Processing frames...'
    else:
        # Stop processing
        if processing_interval:
            clearInterval(processing_interval)
            processing_interval = None
        
        # Clean up the proxy (optional, but good practice)
        if timer_proxy:
            timer_proxy.destroy()
            timer_proxy = None
            
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

# Set up event listeners using create_proxy for proper JavaScript interop
try:
    toggle_btn = document.getElementById('toggleProcessing')
    if toggle_btn:
        toggle_btn.onclick = create_proxy(toggle_processing)
        
    process_btn = document.getElementById('processFrame') 
    if process_btn:
        process_btn.onclick = create_proxy(process_single_frame)
        
    debug_btn = document.getElementById('toggleDebug')
    if debug_btn:
        debug_btn.onclick = create_proxy(toggle_debug_mode)

    # Parameter slider listeners  
    wavelength_slider = document.getElementById('wavelength')
    if wavelength_slider:
        wavelength_slider.oninput = create_proxy(update_parameters)
        
    pixelsize_slider = document.getElementById('pixelsize')
    if pixelsize_slider:
        pixelsize_slider.oninput = create_proxy(update_parameters)
        
    dz_slider = document.getElementById('dz')
    if dz_slider:
        dz_slider.oninput = create_proxy(update_parameters)

    # Initial parameter update
    update_parameters()
    
    console.log("✅ PyScript hologram processing initialized successfully!")
    
    # Test with a single frame to verify everything works
    process_image_for_hologram()
    
except Exception as e:
    console.log(f"❌ Error setting up event listeners: {e}")
    import traceback
    console.log(traceback.format_exc())