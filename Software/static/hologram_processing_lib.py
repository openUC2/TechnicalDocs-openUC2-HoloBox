# Comprehensive Hologram Processing Library for HoloBox
# This module contains all the necessary functions for hologram reconstruction
# Can be used both in PyScript notebooks and Python backends

import numpy as np

class HologramProcessor:
    """
    Comprehensive hologram processing class that handles:
    - Fresnel propagation
    - Image preprocessing
    - Parameter optimization
    - Batch processing
    """
    
    def __init__(self, wavelength=440e-9, pixel_size=1.4e-6):
        """
        Initialize hologram processor with default parameters
        
        Args:
            wavelength: Light wavelength in meters (default: 440nm blue)
            pixel_size: Camera pixel size in meters (default: 1.4µm)
        """
        self.wavelength = wavelength
        self.pixel_size = pixel_size
        
    def abssqr(self, x):
        """Calculate intensity (what a detector sees)"""
        return np.real(x * np.conj(x))
    
    def FT(self, x):
        """Forward Fourier transform with proper frequency shift"""
        return np.fft.fftshift(np.fft.fft2(x))
    
    def iFT(self, x):
        """Inverse Fourier transform with proper frequency shift"""
        return np.fft.ifft2(np.fft.ifftshift(x))
    
    def fresnel_propagator(self, E0, distance, wavelength=None, pixel_size=None):
        """
        Freespace propagation using Fresnel kernel
        
        Args:
            E0: Initial complex field in x-y source plane (2D numpy array)
            distance: Distance from sensor to object in meters
            wavelength: Light wavelength in meters (optional, uses class default)
            pixel_size: Pixel size in meters (optional, uses class default)
        
        Returns:
            Ef: Propagated output field (complex 2D array)
        """
        if wavelength is None:
            wavelength = self.wavelength
        if pixel_size is None:
            pixel_size = self.pixel_size
            
        # Get image dimensions
        upsample_scale = 1
        n = upsample_scale * E0.shape[1]  # Image width in pixels
        grid_size = pixel_size * n        # Grid size in x-direction
        
        # Create frequency grids
        fx = np.linspace(-(n-1)/2*(1/grid_size), (n-1)/2*(1/grid_size), n)
        fy = np.linspace(-(n-1)/2*(1/grid_size), (n-1)/2*(1/grid_size), n)
        Fx, Fy = np.meshgrid(fx, fy)
        
        # Fresnel kernel / point spread function
        H = np.exp(1j*(2 * np.pi / wavelength) * distance) * \
            np.exp(1j * np.pi * wavelength * distance * (Fx**2 + Fy**2))
        
        # Apply Fresnel propagation
        E0fft = self.FT(E0)
        G = H * E0fft
        Ef = self.iFT(G)
        
        return Ef
    
    def preprocess_hologram(self, hologram, normalize=True, crop_size=None):
        """
        Preprocess raw hologram data
        
        Args:
            hologram: Raw hologram data (2D numpy array)
            normalize: Whether to normalize the hologram to [0,1]
            crop_size: Size to crop to (None for no cropping)
        
        Returns:
            Preprocessed hologram as complex field
        """
        # Handle different input formats
        if len(hologram.shape) == 3:
            # RGB image - take first channel
            hologram = hologram[:, :, 0]
        
        # Crop if requested
        if crop_size is not None:
            h, w = hologram.shape
            center_h, center_w = h // 2, w // 2
            half_crop = crop_size // 2
            hologram = hologram[center_h-half_crop:center_h+half_crop,
                              center_w-half_crop:center_w+half_crop]
        
        # Normalize
        if normalize:
            hologram = hologram / np.max(hologram)
        
        # Convert to complex field (amplitude)
        amplitude = np.sqrt(hologram)
        return amplitude.astype(complex)
    
    def reconstruct_hologram(self, hologram, distance, wavelength=None, pixel_size=None, 
                           preprocess=True):
        """
        Complete hologram reconstruction pipeline
        
        Args:
            hologram: Raw hologram data
            distance: Reconstruction distance in meters
            wavelength: Light wavelength in meters (optional)
            pixel_size: Pixel size in meters (optional)
            preprocess: Whether to preprocess the hologram
        
        Returns:
            Dictionary containing:
            - 'intensity': Reconstructed intensity image
            - 'complex_field': Full complex field
            - 'phase': Phase information
            - 'amplitude': Amplitude information
        """
        # Preprocess hologram
        if preprocess:
            complex_field = self.preprocess_hologram(hologram)
        else:
            complex_field = hologram.astype(complex)
        
        # Reconstruct
        reconstructed = self.fresnel_propagator(complex_field, distance, 
                                              wavelength, pixel_size)
        
        # Extract different representations
        intensity = self.abssqr(reconstructed)
        phase = np.angle(reconstructed)
        amplitude = np.abs(reconstructed)
        
        return {
            'intensity': intensity,
            'complex_field': reconstructed,
            'phase': phase,
            'amplitude': amplitude
        }
    
    def find_optimal_distance(self, hologram, distance_range, num_steps=20, 
                            focus_metric='variance'):
        """
        Find optimal reconstruction distance using focus metrics
        
        Args:
            hologram: Raw hologram data
            distance_range: Tuple of (min_distance, max_distance) in meters
            num_steps: Number of distances to test
            focus_metric: Focus metric to use ('variance', 'gradient', 'sobel')
        
        Returns:
            Dictionary with optimal distance and focus scores
        """
        distances = np.linspace(distance_range[0], distance_range[1], num_steps)
        focus_scores = []
        
        # Preprocess hologram once
        complex_field = self.preprocess_hologram(hologram)
        
        for distance in distances:
            # Reconstruct at this distance
            result = self.reconstruct_hologram(complex_field, distance, 
                                             preprocess=False)
            intensity = result['intensity']
            
            # Calculate focus metric
            if focus_metric == 'variance':
                score = np.var(intensity)
            elif focus_metric == 'gradient':
                gx = np.gradient(intensity)[0]
                gy = np.gradient(intensity)[1]
                score = np.mean(gx**2 + gy**2)
            elif focus_metric == 'sobel':
                # Simplified Sobel operator
                gx = np.gradient(intensity, axis=1)
                gy = np.gradient(intensity, axis=0)
                score = np.mean(np.sqrt(gx**2 + gy**2))
            else:
                raise ValueError(f"Unknown focus metric: {focus_metric}")
            
            focus_scores.append(score)
        
        # Find optimal distance
        optimal_idx = np.argmax(focus_scores)
        optimal_distance = distances[optimal_idx]
        
        return {
            'optimal_distance': optimal_distance,
            'distances': distances,
            'focus_scores': focus_scores,
            'optimal_score': focus_scores[optimal_idx]
        }
    
    def create_sample_hologram(self, size=256, objects='circles'):
        """
        Create a synthetic hologram for testing and demonstration
        
        Args:
            size: Size of the hologram (pixels)
            objects: Type of objects to simulate ('circles', 'lines', 'random')
        
        Returns:
            Synthetic hologram as 2D numpy array
        """
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(x, y)
        
        if objects == 'circles':
            # Create some sample objects (circles)
            obj1 = np.exp(-((X-0.3)**2 + (Y-0.2)**2) / 0.01)
            obj2 = np.exp(-((X+0.2)**2 + (Y-0.3)**2) / 0.02)
            obj3 = np.exp(-((X-0.1)**2 + (Y+0.4)**2) / 0.015)
            
            # Add interference patterns
            hologram = 1 + 0.5 * np.cos(10 * np.pi * X) * obj1 + \
                          0.3 * np.cos(15 * np.pi * Y) * obj2 + \
                          0.4 * np.cos(12 * np.pi * (X + Y)) * obj3
                          
        elif objects == 'lines':
            # Create line patterns
            hologram = 1 + 0.3 * np.cos(20 * np.pi * X) + \
                          0.2 * np.cos(25 * np.pi * Y) + \
                          0.4 * np.cos(15 * np.pi * (X + Y))
                          
        elif objects == 'random':
            # Random pattern
            hologram = 1 + 0.5 * np.random.random((size, size))
            # Add some structure
            hologram += 0.3 * np.cos(8 * np.pi * X) * np.cos(8 * np.pi * Y)
            
        else:
            raise ValueError(f"Unknown object type: {objects}")
        
        # Add some noise
        hologram += 0.1 * np.random.random((size, size))
        
        # Ensure positive values
        hologram = np.abs(hologram)
        
        return hologram
    
    def batch_process_distances(self, hologram, distances):
        """
        Process hologram at multiple distances efficiently
        
        Args:
            hologram: Raw hologram data
            distances: List/array of distances to process
        
        Returns:
            List of reconstruction results
        """
        # Preprocess once
        complex_field = self.preprocess_hologram(hologram)
        
        results = []
        for distance in distances:
            result = self.reconstruct_hologram(complex_field, distance, 
                                             preprocess=False)
            results.append(result)
        
        return results

# Convenience functions for direct use
def process_hologram_simple(hologram, distance, wavelength=440e-9, pixel_size=1.4e-6):
    """Simple hologram processing function"""
    processor = HologramProcessor(wavelength, pixel_size)
    return processor.reconstruct_hologram(hologram, distance)

def create_demo_hologram(size=256):
    """Create a demo hologram for testing"""
    processor = HologramProcessor()
    return processor.create_sample_hologram(size)

def find_focus(hologram, min_dist=0.001, max_dist=0.010, steps=20):
    """Find optimal focus distance"""
    processor = HologramProcessor()
    return processor.find_optimal_distance(hologram, (min_dist, max_dist), steps)

# For PyScript compatibility - make functions available globally
try:
    # Check if we're in PyScript environment
    from js import window
    
    # Make key functions available to JavaScript
    from pyodide.ffi import create_proxy
    
    window.HologramProcessor = create_proxy(HologramProcessor)
    window.process_hologram_simple = create_proxy(process_hologram_simple)
    window.create_demo_hologram = create_proxy(create_demo_hologram)
    window.find_focus = create_proxy(find_focus)
    
except ImportError:
    # Not in PyScript environment, that's fine
    pass