#!/usr/bin/env python3
"""
Demo script showing how to start the HoloBox camera system
"""

import sys
import os
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'numpy',
        'cv2',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"✗ {package}")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install fastapi uvicorn numpy opencv-python pydantic")
        if 'picamera2' not in [p.__name__ for p in sys.modules.values() if hasattr(p, '__name__')]:
            print("Note: picamera2 not found - will use mock camera")
        return False
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("\n=== Starting HoloBox Camera API ===")
    
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        api_file = os.path.join(script_dir, 'streamlined_camera_api.py')
        
        if not os.path.exists(api_file):
            print(f"Error: {api_file} not found!")
            return False
        
        print(f"Starting server from: {api_file}")
        print("Server will be available at: http://localhost:8000")
        print("Web interface will be at: http://localhost:8000/static/")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Start the server
        subprocess.run([sys.executable, api_file], check=True)
        
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def show_usage():
    """Show usage instructions"""
    print("HoloBox Camera System Demo")
    print("=" * 40)
    print("\nUsage:")
    print("1. Run this script to start the API server")
    print("2. Open http://localhost:8000/static/ in your browser")
    print("3. Click 'Start Stream' to begin camera streaming")
    print("4. Adjust hologram processing parameters:")
    print("   - Wavelength: 380-700 nm (laser wavelength)")
    print("   - Pixel Size: 0.5-5.0 µm (camera pixel size)")
    print("   - Distance: 0.1-20.0 mm (propagation distance)")
    print("5. Click 'Enable Processing' for real-time hologram reconstruction")
    print("\nFeatures:")
    print("- Real-time MJPEG streaming")
    print("- Camera parameter control (exposure, gain)")
    print("- Client-side Fresnel propagation using PyScript")
    print("- Side-by-side original and processed display")
    print("- JPEG capture and download")
    print("\nNote: Without a real camera, the system will use a mock camera for demonstration.")

def main():
    """Main demo function"""
    print("HoloBox Camera & Hologram Processing System")
    print("=" * 50)
    
    show_usage()
    
    print("\n=== Checking Dependencies ===")
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\nSome dependencies are missing, but the system can still run with mock data.")
        response = input("\nContinue anyway? (y/n): ").lower().strip()
        if response != 'y':
            print("Exiting. Install dependencies and try again.")
            return False
    
    print("\n=== Starting Demo ===")
    response = input("Start the server? (y/n): ").lower().strip()
    if response == 'y':
        return start_server()
    else:
        print("Demo cancelled.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)