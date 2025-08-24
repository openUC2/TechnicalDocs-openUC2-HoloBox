#!/usr/bin/env python3
"""
Download external dependencies for offline use in HoloBox
This script downloads CSS, JavaScript, and PyScript dependencies
to make the web interface work without internet access.
"""

import os
import requests
import sys
from pathlib import Path

def download_file(url, local_path):
    """Download a file from URL to local path"""
    try:
        print(f"Downloading {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"  Saved to {local_path}")
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def main():
    # Get the script directory and set up paths
    script_dir = Path(__file__).parent
    static_dir = script_dir / "static"
    
    # Create static directory if it doesn't exist
    static_dir.mkdir(exist_ok=True)
    
    # Define the external dependencies to download
    dependencies = [
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
            'local_path': static_dir / 'css' / 'bootstrap.min.css'
        },
        {
            'url': 'https://pyscript.net/releases/2025.5.1/core.css',
            'local_path': static_dir / 'css' / 'pyscript-core.css'
        },
        {
            'url': 'https://pyscript.net/releases/2025.5.1/core.js',
            'local_path': static_dir / 'js' / 'pyscript-core.js'
        }
    ]
    
    print("Downloading offline dependencies for HoloBox...")
    print(f"Target directory: {static_dir}")
    print()
    
    success_count = 0
    total_count = len(dependencies)
    
    for dep in dependencies:
        if download_file(dep['url'], dep['local_path']):
            success_count += 1
        print()
    
    print(f"Downloaded {success_count}/{total_count} dependencies successfully.")
    
    if success_count == total_count:
        print("All dependencies downloaded successfully!")
        print("\nNext step: Update index.html to use local dependencies.")
        return 0
    else:
        print(f"Failed to download {total_count - success_count} dependencies.")
        print("Please check your internet connection and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())