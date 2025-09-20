import numpy as np
from js import document, console, ImageData, Uint8ClampedArray, setInterval, clearInterval
from pyodide.ffi import to_js, create_proxy
import asyncio

# Global variables for off-axis processing
# Global variables for off-axis processing
processing_enabled = False
processing_interval = None
timer_proxy = None
current_wavelength = 532e-9  # nm to m (default green)
current_pixelsize = 1.4e-6   # µm to m  
current_refocus_distance = 0.0  # µm (digital refocusing)
debug_mode = True
current_roi = {'x': 100, 'y': 100, 'width': 100, 'height': 100}

console.log("🔧 Starting PyScript off-axis hologram processing setup...")

def process_offaxis_hologram(hologram, roi_coords, wavelength, pixel_size, refocus_distance): False
processing_interval = None
timer_proxy = None
current_wavelength = 532e-9  # nm to m (default green)
current_pixelsize = 1.4e-6   # µm to m  
current_refocus_distance = 0.0  # µm (digital refocusing)
debug_mode = True
current_roi = {'x': 100, 'y': 100, 'width': 100, 'height': 100}

console.log("🔧 Starting PyScript off-axis hologram processing setup...")

def process_offaxis_hologram(hologram, roi_coords, wavelength, pixel_size, refocus_distance):
    """
    Complete off-axis hologram reconstruction pipeline
    
    Args:
        hologram: 2D numpy array of hologram intensity
        roi_coords: dict with 'x', 'y', 'width', 'height' of cross-correlation term
        wavelength: illumination wavelength in meters
        pixel_size: camera pixel size in meters  
        refocus_distance: digital refocusing distance in meters
    
    Returns:
        dict with 'amplitude', 'phase', 'fourier_magnitude' arrays
    """
    try:
        if debug_mode:
            console.log(f"Processing hologram shape: {hologram.shape}")
            console.log(f"ROI: {roi_coords}")
            console.log(f"Wavelength: {wavelength*1e9:.1f}nm, Pixel size: {pixel_size*1e6:.1f}µm")
        
        # Step 1: Fourier transform
        H = np.fft.fftshift(np.fft.fft2(hologram))
        fourier_magnitude = np.abs(H)
        
        if debug_mode:
            console.log(f"Fourier transform shape: {H.shape}")
            console.log(f"Fourier magnitude range: {fourier_magnitude.min():.2f} - {fourier_magnitude.max():.2f}")
        
        # Step 2: Extract cross-correlation term using ROI
        x, y, w, h = roi_coords['x'], roi_coords['y'], roi_coords['width'], roi_coords['height']
        
        # Ensure ROI is within bounds
        x = max(0, min(x, H.shape[1] - w))
        y = max(0, min(y, H.shape[0] - h))
        w = min(w, H.shape[1] - x)
        h = min(h, H.shape[0] - y)
        
        H_cropped = np.zeros_like(H)
        H_cropped[y:y+h, x:x+w] = H[y:y+h, x:x+w]
        
        if debug_mode:
            console.log(f"Cropped region: x={x}, y={y}, w={w}, h={h}")
        
        # Step 3: Center the cropped term (translate to center frequency)
        center_y, center_x = H.shape[0]//2, H.shape[1]//2
        roi_center_y, roi_center_x = y + h//2, x + w//2
        
        # Calculate shift needed to center the ROI
        shift_y = center_y - roi_center_y
        shift_x = center_x - roi_center_x
        
        H_centered = np.roll(H_cropped, (shift_y, shift_x), axis=(0, 1))
        
        # Step 4: Inverse Fourier transform to get complex field
        field = np.fft.ifft2(np.fft.ifftshift(H_centered))
        
        # Step 5: Digital refocusing if distance is non-zero
        if abs(refocus_distance) > 1e-9:  # Only if distance > 1nm
            field = apply_digital_refocus(field, wavelength, pixel_size, refocus_distance)
        
        # Calculate amplitude and phase
        amplitude = np.abs(field)
        phase = np.angle(field)
        
        if debug_mode:
            console.log(f"Reconstruction completed")
            console.log(f"Amplitude range: {amplitude.min():.3f} - {amplitude.max():.3f}")
            console.log(f"Phase range: {phase.min():.3f} - {phase.max():.3f}")
        
        return {
            'fourier_magnitude': np.log(1+fourier_magnitude/np.max(fourier_magnitude))*255.,  # Log scale for better visualization
            'amplitude': amplitude,
            'phase': phase
        }
        
    except Exception as e:
        console.log(f"❌ Error in off-axis processing: {e}")
        import traceback
        console.log(traceback.format_exc())
        return None

def apply_digital_refocus(field, wavelength, pixel_size, z):
    """Apply Fresnel propagation for digital refocusing"""
    try:
        Ny, Nx = field.shape
        
        # Coordinate grids
        x = (np.arange(Nx) - Nx//2) * pixel_size
        y = (np.arange(Ny) - Ny//2) * pixel_size
        X, Y = np.meshgrid(x, y)
        
        # Fresnel phase factor
        k = 2 * np.pi / wavelength
        phase_factor = np.exp(1j * k / (2 * z) * (X**2 + Y**2))
        
        if debug_mode:
            console.log(f"Applied digital refocus: z={z*1e6:.1f}µm")
        
        return field * phase_factor
        
    except Exception as e:
        console.log(f"❌ Error in digital refocus: {e}")
        return field

def create_window_mask(shape, center, size, window_type='rectangular'):
    """Create different types of selection windows"""
    try:
        mask = np.zeros(shape)
        cy, cx = center
        hy, hx = size
        
        if window_type == 'rectangular':
            y1, y2 = max(0, cy - hy//2), min(shape[0], cy + hy//2)
            x1, x2 = max(0, cx - hx//2), min(shape[1], cx + hx//2)
            mask[y1:y2, x1:x2] = 1
            
        elif window_type == 'circular':
            y, x = np.ogrid[:shape[0], :shape[1]]
            radius = min(hx, hy) // 2
            mask[(x - cx)**2 + (y - cy)**2 <= radius**2] = 1
            
        elif window_type == 'gaussian':
            y, x = np.ogrid[:shape[0], :shape[1]]
            sigma_x, sigma_y = hx/4, hy/4
            mask = np.exp(-((x - cx)**2/(2*sigma_x**2) + (y - cy)**2/(2*sigma_y**2)))
        
        return mask
        
    except Exception as e:
        console.log(f"❌ Error creating window mask: {e}")
        return np.ones(shape)

def display_image_on_canvas(image_array, canvas_id, colormap='gray'):
    """Display a 2D numpy array on a canvas with optional colormap"""
    try:
        canvas = document.getElementById(canvas_id)
        if not canvas:
            console.log(f"❌ Canvas {canvas_id} not found")
            return
            
        ctx = canvas.getContext('2d')
        height, width = image_array.shape
        
        # Normalize image to 0-255 range
        if image_array.max() > image_array.min():
            normalized = ((image_array - image_array.min()) / 
                         (image_array.max() - image_array.min()) * 255).astype(np.uint8)
        else:
            normalized = np.zeros_like(image_array, dtype=np.uint8)
        
        # Create RGBA data
        if colormap == 'gray':
            # Grayscale
            rgba_data = np.zeros((height, width, 4), dtype=np.uint8)
            rgba_data[:, :, 0] = normalized  # R
            rgba_data[:, :, 1] = normalized  # G
            rgba_data[:, :, 2] = normalized  # B
            rgba_data[:, :, 3] = 255        # Alpha
        elif colormap == 'phase':
            # Phase colormap (HSV-like)
            # Map phase (-π to π) to hue (0 to 360 degrees)
            hue = ((image_array + np.pi) / (2 * np.pi) * 360).astype(np.int32)
            hue = np.clip(hue, 0, 359)  # Ensure values are within bounds
            rgba_data = np.zeros((height, width, 4), dtype=np.uint8)
            
            # Simple HSV to RGB conversion for phase visualization
            for i in range(height):
                for j in range(width):
                    h = hue[i, j]
                    if h < 120:  # Red to Green
                        rgba_data[i, j, 0] = min(255, max(0, 255 - int(h * 255 // 120)))
                        rgba_data[i, j, 1] = min(255, max(0, int(h * 255 // 120)))
                        rgba_data[i, j, 2] = 0
                    elif h < 240:  # Green to Blue
                        rgba_data[i, j, 0] = 0
                        rgba_data[i, j, 1] = min(255, max(0, 255 - int((h - 120) * 255 // 120)))
                        rgba_data[i, j, 2] = min(255, max(0, int((h - 120) * 255 // 120)))
                    else:  # Blue to Red
                        rgba_data[i, j, 0] = min(255, max(0, int((h - 240) * 255 // 120)))
                        rgba_data[i, j, 1] = 0
                        rgba_data[i, j, 2] = min(255, max(0, 255 - int((h - 240) * 255 // 120)))
                    rgba_data[i, j, 3] = 255
        
        # Resize canvas to match image
        canvas.width = width
        canvas.height = height
        
        # Convert to JavaScript ImageData
        image_data = ctx.createImageData(width, height)
        js_array = to_js(rgba_data.flatten().tolist())
        image_data.data.set(js_array)
        
        # Draw to canvas
        ctx.putImageData(image_data, 0, 0)
        
        if debug_mode:
            console.log(f"✅ Image displayed on {canvas_id}")
            
    except Exception as e:
        console.log(f"❌ Error displaying image on {canvas_id}: {e}")
        import traceback
        console.log(traceback.format_exc())

def get_camera_image():
    """Get current camera image for processing"""
    try:
        # Try to get the stream image (use 'stream' ID for consistency)
        stream_img = document.getElementById("stream")
        
        if debug_mode:
            if stream_img:
                console.log(f"Debug: Stream element found - complete: {stream_img.complete}, naturalWidth: {stream_img.naturalWidth}, src: {stream_img.src}")
            else:
                console.log("Debug: Stream element with ID 'stream' not found")
        
        if stream_img and stream_img.complete and stream_img.naturalWidth > 0 and stream_img.src and not stream_img.src.startswith('data:,'):
            # Create a canvas to extract image data
            temp_canvas = document.createElement('canvas')
            temp_ctx = temp_canvas.getContext('2d')
            temp_canvas.width = stream_img.naturalWidth
            temp_canvas.height = stream_img.naturalHeight
            
            # Draw image to canvas
            temp_ctx.drawImage(stream_img, 0, 0)
            
            # Get image data
            image_data = temp_ctx.getImageData(0, 0, temp_canvas.width, temp_canvas.height)
            width, height = temp_canvas.width, temp_canvas.height
            
            # Convert JavaScript ImageData to numpy array
            # Use numpy.array() directly on the JS array
            rgba_array = np.array(image_data.data.to_py(), dtype=np.uint8)
            rgba_array = rgba_array.reshape((height, width, 4))
            
            # Use green channel for hologram processing
            hologram = rgba_array[:, :, 1].astype(np.float64)
            
            if debug_mode:
                console.log(f"✅ Got camera image: {width}x{height}")
                console.log(f"Image data shape: {rgba_array.shape}")
                console.log(f"Hologram range: {hologram.min():.1f} - {hologram.max():.1f}")
                
            return hologram
            
        else:
            if debug_mode:
                console.log("Debug: Camera stream not available, creating synthetic hologram")
            
            # Create synthetic off-axis hologram for testing
            width, height = 400, 400
            
            # Create interference pattern
            y, x = np.mgrid[0:height, 0:width]
            
            # Object beam (central spot)
            object_beam = np.exp(-((x-200)**2 + (y-200)**2) / (2*30**2))
            
            # Reference beam (tilted plane wave)
            reference_beam = np.exp(1j * 0.05 * (x + y))
            
            # Interference pattern (hologram intensity)
            total_field = object_beam + 0.8 * reference_beam
            hologram = np.abs(total_field)**2
            
            # Add some noise
            hologram += 0.1 * np.random.random((height, width))
            
            if debug_mode:
                console.log(f"✅ Created synthetic hologram: {width}x{height}")
                
            return hologram
            
    except Exception as e:
        console.log(f"❌ Error getting camera image: {e}")
        return None

def process_current_frame():
    """Process current frame for off-axis reconstruction"""
    try:
        if debug_mode:
            console.log("🔄 Processing current frame...")
        
        # Get current camera image
        hologram = get_camera_image()
        if hologram is None:
            console.log("❌ Failed to get camera image")
            return
        
        # Get current ROI from UI
        roi_x = int(document.getElementById('roi-x').value)
        roi_y = int(document.getElementById('roi-y').value)
        roi_width = int(document.getElementById('roi-width').value)
        roi_height = int(document.getElementById('roi-height').value)
        
        roi_coords = {
            'x': roi_x,
            'y': roi_y, 
            'width': roi_width,
            'height': roi_height
        }
        
        # Process the hologram
        results = process_offaxis_hologram(
            hologram, 
            roi_coords, 
            current_wavelength, 
            current_pixelsize, 
            current_refocus_distance * 1e-6  # Convert µm to m
        )
        
        if results:
            # Display results on canvases
            display_image_on_canvas(results['fourier_magnitude'], 'fourier-canvas', 'gray')
            display_image_on_canvas(results['amplitude'], 'amplitude-canvas', 'gray')
            display_image_on_canvas(results['phase'], 'phase-canvas', 'phase')
            
            if debug_mode:
                console.log("✅ Frame processing completed")
        
    except Exception as e:
        console.log(f"❌ Error processing current frame: {e}")
        import traceback
        console.log(traceback.format_exc())

def toggle_processing(event=None):
    """Toggle off-axis processing on/off"""
    global processing_enabled, processing_interval, timer_proxy
    
    try:
        processing_enabled = not processing_enabled
        toggle_btn = document.getElementById('toggleProcessing')
        
        if processing_enabled:
            toggle_btn.textContent = 'Disable Processing'
            toggle_btn.className = 'btn btn-danger'
            
            # Start processing timer
            def process_timer():
                process_current_frame()
            
            timer_proxy = create_proxy(process_timer)
            processing_interval = setInterval(timer_proxy, 500)  # Process every 500ms
            console.log("✅ Off-axis processing enabled")
            
        else:
            toggle_btn.textContent = 'Enable Processing'
            toggle_btn.className = 'btn btn-info'
            
            if processing_interval:
                clearInterval(processing_interval)
                processing_interval = None
            console.log("⏹️ Off-axis processing disabled")
            
    except Exception as e:
        console.log(f"❌ Error toggling processing: {e}")

def process_single_frame(event=None):
    """Process a single frame"""
    try:
        console.log("🔄 Processing single frame...")
        process_current_frame()
    except Exception as e:
        console.log(f"❌ Error processing single frame: {e}")

def toggle_debug_mode(event=None):
    """Toggle debug mode on/off"""
    global debug_mode
    try:
        debug_mode = not debug_mode
        debug_btn = document.getElementById('toggleDebug')
        
        if debug_mode:
            debug_btn.textContent = 'Disable Debug'
            debug_btn.className = 'btn btn-warning'
            console.log("🐛 Debug mode enabled")
        else:
            debug_btn.textContent = 'Enable Debug'
            debug_btn.className = 'btn btn-outline-warning'
            console.log("🐛 Debug mode disabled")
            
    except Exception as e:
        console.log(f"❌ Error toggling debug mode: {e}")

def update_parameters(event=None):
    """Update processing parameters from sliders"""
    global current_wavelength, current_pixelsize, current_refocus_distance
    
    try:
        # Update wavelength
        wavelength_slider = document.getElementById('wavelength')
        if wavelength_slider:
            current_wavelength = float(wavelength_slider.value) * 1e-9  # nm to m
            document.getElementById('wavelength-value').textContent = wavelength_slider.value
        
        # Update pixel size
        pixelsize_slider = document.getElementById('pixelsize')
        if pixelsize_slider:
            current_pixelsize = float(pixelsize_slider.value) * 1e-6  # µm to m
            document.getElementById('pixelsize-value').textContent = pixelsize_slider.value
            
        # Update refocus distance
        refocus_slider = document.getElementById('refocus-distance')
        if refocus_slider:
            current_refocus_distance = float(refocus_slider.value)  # Already in µm
            document.getElementById('refocus-distance-value').textContent = refocus_slider.value
        
        if debug_mode:
            console.log(f"📐 Parameters updated: λ={current_wavelength*1e9:.0f}nm, px={current_pixelsize*1e6:.1f}µm, z={current_refocus_distance:.0f}µm")
        
    except Exception as e:
        console.log(f"❌ Error updating parameters: {e}")

# Set up event listeners using create_proxy for proper JavaScript interop
try:
    # Processing controls
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
        
    refocus_slider = document.getElementById('refocus-distance')
    if refocus_slider:
        refocus_slider.oninput = create_proxy(update_parameters)

    # Initial parameter update
    update_parameters()
    
    # Make process function available globally for JavaScript
    from js import window
    window.processCurrentFrame = create_proxy(process_current_frame)
    
    console.log("✅ PyScript off-axis hologram processing initialized successfully!")
    
    # Test with a single frame to verify everything works
    process_current_frame()
    
except Exception as e:
    console.log(f"❌ Error setting up off-axis event listeners: {e}")
    import traceback
    console.log(traceback.format_exc())