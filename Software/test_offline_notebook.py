#!/usr/bin/env python3
"""
Test the offline Jupyter notebook implementation for HoloBox
"""

import os
import sys
import subprocess
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("=== Testing File Structure ===")
    
    static_dir = Path("static")
    required_files = [
        "notebook.html",
        "hologram_processing_lib.py",
        "README.md",
        "vendor/bootstrap.min.css",
        "vendor/pyscript-core.css",
        "vendor/pyscript-core.js"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = static_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files exist")
        return True

def test_html_structure():
    """Test HTML structure and references"""
    print("\n=== Testing HTML Structure ===")
    
    try:
        with open("static/notebook.html", "r") as f:
            content = f.read()
        
        checks = [
            ('vendor/bootstrap.min.css', "Bootstrap CSS reference"),
            ('vendor/pyscript-core.css', "PyScript CSS reference"),
            ('vendor/pyscript-core.js', "PyScript JS reference"),
            ('hologram_processing_lib.py', "Hologram library reference"),
            ('<py-config>', "PyScript configuration"),
            ('<py-script>', "PyScript code block"),
            ('HoloBox Jupyter Notebook', "Title present"),
            ('notebook-cell', "Notebook cell structure"),
            ('Run All Cells', "Run all button"),
            ('processHologram', "Process button"),
            ('generateSample', "Generate button"),
        ]
        
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ Missing: {description}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return False

def test_python_syntax():
    """Test Python library syntax"""
    print("\n=== Testing Python Library Syntax ===")
    
    try:
        # Test if the Python file compiles
        with open("static/hologram_processing_lib.py", "r") as f:
            code = f.read()
        
        compile(code, "hologram_processing_lib.py", "exec")
        print("✅ Python library compiles successfully")
        
        # Test key class and function definitions
        checks = [
            ('class HologramProcessor:', "HologramProcessor class"),
            ('def fresnel_propagator(', "Fresnel propagation function"),
            ('def reconstruct_hologram(', "Reconstruction function"),
            ('def find_optimal_distance(', "Auto-focus function"),
            ('def create_sample_hologram(', "Sample generation function"),
            ('import numpy as np', "NumPy import"),
        ]
        
        all_good = True
        for check, description in checks:
            if check in code:
                print(f"✅ {description}")
            else:
                print(f"❌ Missing: {description}")
                all_good = False
        
        return all_good
        
    except SyntaxError as e:
        print(f"❌ Syntax error in Python library: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Python library: {e}")
        return False

def test_offline_capabilities():
    """Test offline capability features"""
    print("\n=== Testing Offline Capabilities ===")
    
    try:
        with open("static/notebook.html", "r") as f:
            content = f.read()
        
        # Check for fallback mechanisms
        checks = [
            ('onerror=', "CSS fallback mechanism"),
            ('cdn.jsdelivr.net', "CDN fallback present"),
            ('pyscript.net', "PyScript CDN fallback"),
            ('vendor/', "Local vendor directory references"),
        ]
        
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ Missing: {description}")
                all_good = False
        
        # Check vendor files have content
        vendor_files = [
            "static/vendor/bootstrap.min.css",
            "static/vendor/pyscript-core.css", 
            "static/vendor/pyscript-core.js"
        ]
        
        for file in vendor_files:
            if os.path.exists(file) and os.path.getsize(file) > 100:
                print(f"✅ {file} has content")
            else:
                print(f"❌ {file} missing or empty")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error testing offline capabilities: {e}")
        return False

def test_integration_points():
    """Test integration with existing system"""
    print("\n=== Testing Integration Points ===")
    
    try:
        # Check if existing files still exist
        existing_files = [
            "static/index.html",
            "static/camera_controls.js",
            "static/hologram_processing.py"
        ]
        
        all_good = True
        for file in existing_files:
            if os.path.exists(file):
                print(f"✅ Existing file preserved: {file}")
            else:
                print(f"⚠️  Existing file missing: {file}")
                # Not necessarily an error, but worth noting
        
        # Check README documentation
        if os.path.exists("static/README.md"):
            with open("static/README.md", "r") as f:
                readme_content = f.read()
            
            if len(readme_content) > 1000:
                print("✅ Comprehensive README documentation")
            else:
                print("❌ README too short")
                all_good = False
        else:
            print("❌ README missing")
            all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def main():
    """Run all tests"""
    print("HoloBox Offline Notebook Test Suite")
    print("=" * 50)
    
    # Change to Software directory if needed
    if not os.path.exists("static"):
        if os.path.exists("Software/static"):
            os.chdir("Software")
        else:
            print("❌ Cannot find static directory")
            return False
    
    tests = [
        ("File Structure", test_file_structure),
        ("HTML Structure", test_html_structure), 
        ("Python Library", test_python_syntax),
        ("Offline Capabilities", test_offline_capabilities),
        ("Integration Points", test_integration_points)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n❌ {test_name}: ERROR - {e}")
        
        print("-" * 30)
    
    print(f"\nTest Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Offline notebook is ready.")
        return True
    else:
        print("❌ Some tests failed. Check issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)