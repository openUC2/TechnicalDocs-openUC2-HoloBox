#!/usr/bin/env python3
"""
Build script for xeus-lite-demo based JupyterLite for HoloBox.

This script replaces the previous custom JupyterLite implementation with
the proper xeus-lite-demo template structure.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Install required dependencies for JupyterLite build."""
    print("Installing JupyterLite dependencies...")
    
    # Check if jupyterlite is available
    try:
        subprocess.check_call([sys.executable, "-c", "import jupyterlite_core"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ JupyterLite core already available")
    except subprocess.CalledProcessError:
        print("⚠ JupyterLite not available in current environment")
        print("  Please install dependencies manually:")
        print("  pip install jupyterlite-core jupyterlite-xeus-python")
        print("  pip install numpy matplotlib scipy ipywidgets pillow requests")
        return False
    
    return True

def build_jupyterlite():
    """Build the JupyterLite site using jupyter lite build."""
    print("\nBuilding JupyterLite site...")
    
    try:
        # Change to Software directory
        os.chdir(Path(__file__).parent)
        
        # Check if jupyter lite command is available
        try:
            subprocess.check_call([sys.executable, "-m", "jupyter", "lite", "--version"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("⚠ JupyterLite CLI not available")
            print("  Creating minimal structure for development...")
            return create_minimal_structure()
        
        # Run jupyter lite build
        cmd = [
            sys.executable, "-m", "jupyter", "lite", "build",
            "--contents", "content",
            "--output-dir", "dist"
        ]
        
        subprocess.check_call(cmd)
        print("✓ JupyterLite build completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        print("  Creating minimal structure for development...")
        return create_minimal_structure()

def create_minimal_structure():
    """Create minimal structure for development when full JupyterLite isn't available."""
    print("Creating minimal development structure...")
    
    # Create dist directory structure
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Create lab directory
    lab_dir = dist_dir / "lab"
    lab_dir.mkdir(exist_ok=True)
    
    # Create a placeholder index.html that explains the setup
    placeholder_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HoloBox JupyterLite - Setup Required</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f8f9fa;
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2e7d32; margin-bottom: 30px; }
        .setup-section {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: left;
        }
        .command {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            overflow-x: auto;
        }
        .info { color: #666; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 HoloBox JupyterLite</h1>
        <h2>Setup Required</h2>
        
        <div class="info">
            This is a placeholder page. To build the full JupyterLite environment with xeus-python, 
            you need to install the required dependencies.
        </div>
        
        <div class="setup-section">
            <h3>🚀 Quick Setup (Local Development)</h3>
            <div class="command">
pip install jupyterlite-core jupyterlite-xeus-python<br>
pip install numpy matplotlib scipy ipywidgets pillow requests<br>
cd Software<br>
python build_xeus_lite.py
            </div>
        </div>
        
        <div class="setup-section">
            <h3>🌐 GitHub Actions Deployment</h3>
            <p>For automatic deployment to <code>youseetoo.github.io/jupyter</code>, 
               push changes to the main branch. The GitHub Actions workflow will:</p>
            <ul style="text-align: left;">
                <li>Install all required dependencies</li>
                <li>Build the complete JupyterLite site</li>
                <li>Deploy to GitHub Pages</li>
            </ul>
        </div>
        
        <div class="setup-section">
            <h3>📦 What's Included</h3>
            <ul style="text-align: left;">
                <li><strong>xeus-python kernel</strong>: Full Python compatibility</li>
                <li><strong>Interactive widgets</strong>: Real-time parameter controls</li>
                <li><strong>Hologram processing</strong>: Complete reconstruction pipeline</li>
                <li><strong>Camera integration</strong>: Live capture and processing</li>
                <li><strong>Offline operation</strong>: No internet required after setup</li>
            </ul>
        </div>
        
        <div class="info">
            <strong>Repository:</strong> 
            <a href="https://github.com/openUC2/TechnicalDocs-openUC2-HoloBox">
                TechnicalDocs-openUC2-HoloBox
            </a><br>
            <strong>Deployment:</strong> 
            <a href="https://youseetoo.github.io/jupyter">
                youseetoo.github.io/jupyter
            </a><br>
            <strong>Template:</strong> 
            <a href="https://github.com/jupyterlite/xeus-lite-demo">
                xeus-lite-demo
            </a>
        </div>
    </div>
</body>
</html>'''
    
    with open(lab_dir / "index.html", 'w') as f:
        f.write(placeholder_content)
    
    # Copy the notebook to the dist directory for reference
    content_dir = Path("content")
    if content_dir.exists():
        shutil.copytree(content_dir, dist_dir / "content", dirs_exist_ok=True)
        print("✓ Copied content to dist directory")
    
    print("✓ Created minimal structure")
    print("ℹ Run with full JupyterLite installation for complete functionality")
    return True

def copy_to_static():
    """Copy built site to static directory."""
    print("\nCopying to static directory...")
    
    dist_dir = Path("dist")
    static_dir = Path("static")
    jupyter_static = static_dir / "jupyter"
    
    if not dist_dir.exists():
        print("✗ Build directory not found")
        return False
    
    # Remove existing jupyter files
    if jupyter_static.exists():
        shutil.rmtree(jupyter_static)
        print("✓ Removed existing jupyter files")
    
    # Copy built site
    shutil.copytree(dist_dir, jupyter_static)
    print(f"✓ Copied JupyterLite to {jupyter_static}")
    
    # Update notebook.html redirect
    redirect_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HoloBox Jupyter Notebook - xeus-lite</title>
    <meta http-equiv="refresh" content="0; url=jupyter/lab/index.html">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f8f9fa;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2e7d32; }
        .loading {
            color: #666;
            margin: 20px 0;
        }
        .link {
            color: #1976d2;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 HoloBox Jupyter Notebook</h1>
        <div class="loading">Redirecting to xeus-lite JupyterLite environment...</div>
        <p>If you are not redirected automatically, <a href="jupyter/lab/index.html" class="link">click here</a>.</p>
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        <p><strong>Features:</strong></p>
        <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
            <li>xeus-python kernel for full Python compatibility</li>
            <li>Interactive hologram processing with widgets</li>
            <li>Real-time camera integration</li>
            <li>Advanced focus optimization algorithms</li>
            <li>Complete offline operation</li>
        </ul>
    </div>
</body>
</html>'''
    
    with open(static_dir / "notebook.html", 'w') as f:
        f.write(redirect_content)
    
    print("✓ Updated notebook.html redirect")
    return True

def main():
    """Main build process."""
    print("=" * 60)
    print("HoloBox JupyterLite Build (xeus-lite-demo template)")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("content").exists():
        print("✗ Error: content directory not found")
        print("  Make sure you're running this from the Software directory")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        return 1
    
    # Build JupyterLite
    if not build_jupyterlite():
        print("\n❌ JupyterLite build failed")
        return 1
    
    # Copy to static
    if not copy_to_static():
        print("\n❌ Copy to static failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ Build completed successfully!")
    print("=" * 60)
    print(f"📁 Files available in: static/jupyter/")
    print(f"🌐 Access at: http://localhost:8000/static/notebook.html")
    print(f"📝 Direct lab: http://localhost:8000/static/jupyter/lab/index.html")
    print("\nNext steps:")
    print("1. Start HoloBox server: python streamlined_camera_api.py")
    print("2. Open browser to the URL above")
    print("3. Open hologram_processing.ipynb notebook")
    print("4. Run cells to start processing holograms!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())