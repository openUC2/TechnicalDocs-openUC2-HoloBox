"""
Example integration of the offline notebook with live camera processing
This shows how to integrate the hologram processing library with the main HoloBox system
"""

# This would be added to the main streamlined_camera_api.py

from static.hologram_processing_lib import HologramProcessor
import numpy as np

class HologramIntegration:
    """Integration class for live hologram processing"""
    
    def __init__(self):
        self.processor = HologramProcessor()
        self.current_distance = 0.005  # 5mm default
        self.auto_focus_enabled = False
        
    def process_camera_frame(self, camera_frame):
        """Process a live camera frame for hologram reconstruction"""
        try:
            # Convert camera frame to hologram format
            if len(camera_frame.shape) == 3:
                # RGB to grayscale
                hologram = np.mean(camera_frame, axis=2)
            else:
                hologram = camera_frame
            
            # Process hologram
            results = self.processor.reconstruct_hologram(
                hologram, 
                self.current_distance
            )
            
            return {
                'original': hologram,
                'reconstructed': results['intensity'],
                'phase': results['phase'],
                'amplitude': results['amplitude']
            }
            
        except Exception as e:
            print(f"Error processing hologram: {e}")
            return None
    
    def auto_focus(self, camera_frame):
        """Find optimal focus distance for current frame"""
        try:
            if len(camera_frame.shape) == 3:
                hologram = np.mean(camera_frame, axis=2)
            else:
                hologram = camera_frame
                
            focus_result = self.processor.find_optimal_distance(
                hologram, 
                (0.001, 0.020),  # 1-20mm range
                num_steps=15
            )
            
            self.current_distance = focus_result['optimal_distance']
            return focus_result
            
        except Exception as e:
            print(f"Error in auto-focus: {e}")
            return None
    
    def update_parameters(self, wavelength=None, pixel_size=None, distance=None):
        """Update processing parameters"""
        if wavelength:
            self.processor.wavelength = wavelength * 1e-9  # nm to m
        if pixel_size:
            self.processor.pixel_size = pixel_size * 1e-6  # µm to m
        if distance:
            self.current_distance = distance * 1e-3  # mm to m

# Example FastAPI endpoints that could be added:

"""
@app.post("/hologram/process")
async def process_hologram():
    '''Process current camera frame as hologram'''
    global hologram_integration
    
    if not hologram_integration:
        hologram_integration = HologramIntegration()
    
    # Get current frame from camera
    frame = get_current_camera_frame()  # This would get the current frame
    
    # Process as hologram
    results = hologram_integration.process_camera_frame(frame)
    
    if results:
        return {
            "success": True,
            "distance": hologram_integration.current_distance,
            "shape": results['reconstructed'].shape,
            "intensity_range": [
                float(results['reconstructed'].min()), 
                float(results['reconstructed'].max())
            ]
        }
    else:
        return {"success": False, "error": "Processing failed"}

@app.post("/hologram/autofocus")
async def autofocus_hologram():
    '''Auto-focus hologram reconstruction'''
    global hologram_integration
    
    if not hologram_integration:
        hologram_integration = HologramIntegration()
    
    frame = get_current_camera_frame()
    focus_result = hologram_integration.auto_focus(frame)
    
    if focus_result:
        return {
            "success": True,
            "optimal_distance": focus_result['optimal_distance'],
            "focus_score": focus_result['optimal_score'],
            "tested_distances": focus_result['distances'].tolist()
        }
    else:
        return {"success": False, "error": "Auto-focus failed"}

@app.post("/hologram/parameters")
async def update_hologram_parameters(params: dict):
    '''Update hologram processing parameters'''
    global hologram_integration
    
    if not hologram_integration:
        hologram_integration = HologramIntegration()
    
    hologram_integration.update_parameters(
        wavelength=params.get('wavelength'),
        pixel_size=params.get('pixel_size'),
        distance=params.get('distance')
    )
    
    return {
        "success": True,
        "current_wavelength": hologram_integration.processor.wavelength * 1e9,
        "current_pixel_size": hologram_integration.processor.pixel_size * 1e6,
        "current_distance": hologram_integration.current_distance * 1e3
    }

@app.get("/hologram/stream")
async def hologram_stream():
    '''Stream reconstructed holograms'''
    def generate_hologram_frames():
        global hologram_integration
        
        if not hologram_integration:
            hologram_integration = HologramIntegration()
        
        while True:
            try:
                # Get camera frame
                frame = get_current_camera_frame()
                
                # Process hologram
                results = hologram_integration.process_camera_frame(frame)
                
                if results:
                    # Convert to JPEG
                    reconstructed = results['reconstructed']
                    
                    # Normalize to 0-255
                    normalized = ((reconstructed - reconstructed.min()) / 
                                (reconstructed.max() - reconstructed.min()) * 255).astype(np.uint8)
                    
                    # Encode as JPEG
                    _, jpeg_data = cv2.imencode('.jpg', normalized)
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + 
                           jpeg_data.tobytes() + b'\r\n')
                
                time.sleep(0.1)  # Limit to ~10 FPS
                
            except Exception as e:
                print(f"Error in hologram stream: {e}")
                time.sleep(1)
    
    return StreamingResponse(
        generate_hologram_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
"""

# Usage example:
"""
# In the main application initialization:
hologram_integration = None

# Then the endpoints above can be used to:
# 1. Process individual frames: POST /hologram/process
# 2. Auto-focus: POST /hologram/autofocus  
# 3. Update parameters: POST /hologram/parameters
# 4. Stream reconstructed holograms: GET /hologram/stream
"""

# JavaScript integration for the main interface:
"""
// Add to camera_controls.js or create new hologram_controls.js

// Process current frame as hologram
const processHologram = async () => {
    try {
        const response = await fetch(baseUrl + '/hologram/process', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            console.log(`Hologram processed at distance: ${result.distance}m`);
            document.getElementById('status').textContent = 
                `Hologram processed (${result.distance*1000:.1f}mm)`;
        }
    } catch (error) {
        console.error('Error processing hologram:', error);
    }
};

// Auto-focus hologram
const autoFocusHologram = async () => {
    try {
        const response = await fetch(baseUrl + '/hologram/autofocus', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            console.log(`Auto-focused to: ${result.optimal_distance}m`);
            document.getElementById('status').textContent = 
                `Auto-focused (${result.optimal_distance*1000:.1f}mm)`;
        }
    } catch (error) {
        console.error('Error in auto-focus:', error);
    }
};

// Update hologram parameters from notebook
const updateHologramParameters = async (wavelength, pixelSize, distance) => {
    try {
        const response = await fetch(baseUrl + '/hologram/parameters', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                wavelength: wavelength,
                pixel_size: pixelSize,
                distance: distance
            })
        });
        const result = await response.json();
        
        if (result.success) {
            console.log('Hologram parameters updated');
        }
    } catch (error) {
        console.error('Error updating parameters:', error);
    }
};

// Display hologram stream
const showHologramStream = () => {
    const img = document.getElementById('hologram-stream');
    if (img) {
        img.src = baseUrl + '/hologram/stream';
    }
};
"""