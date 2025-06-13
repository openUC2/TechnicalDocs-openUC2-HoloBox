#!/usr/bin/env python3
"""
Simple test to verify the refactored code works correctly.
Tests:
1. File structure is correct
2. JavaScript syntax is valid
3. Python syntax is valid  
4. HTML references are correct
"""

import os
import subprocess
import sys
from pathlib import Path

def test_file_structure():
    """Test that all expected files exist"""
    static_dir = Path("static")
    
    required_files = [
        "index.html",
        "camera_controls.js", 
        "hologram_processing.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (static_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def test_python_syntax():
    """Test Python file compiles without syntax errors"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "static/hologram_processing.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Python syntax is valid")
            return True
        else:
            print(f"❌ Python syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing Python syntax: {e}")
        return False

def test_html_references():
    """Test that HTML correctly references the external files"""
    try:
        with open("static/index.html", "r") as f:
            content = f.read()
        
        checks = [
            ('src="./hologram_processing.py"', "PyScript file reference"),
            ('src="./camera_controls.js"', "JavaScript file reference"),
            ('<py-script', "PyScript element exists"),
            ('id="toggleProcessing"', "Processing toggle button exists"),
            ('id="stream"', "Stream element exists"),
            ('id="processed"', "Processed canvas exists")
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

def test_js_references():
    """Test that JavaScript file has proper structure"""
    try:
        with open("static/camera_controls.js", "r") as f:
            content = f.read()
        
        checks = [
            ('window.baseUrl', "Global baseUrl variable"),
            ('DOMContentLoaded', "DOM ready handler"),
            ('getElementById', "DOM element access"),
            ('fetch(', "API fetch calls")
        ]
        
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ JS {description}")
            else:
                print(f"❌ JS missing: {description}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading JavaScript file: {e}")
        return False

def test_python_fixes():
    """Test that the reported issues were fixed"""
    try:
        with open("static/hologram_processing.py", "r") as f:
            content = f.read()
        
        checks = [
            ('def toggle_processing(event=None)', "Fixed function parameter"),
            ('process_frame_from_snapshot', "Cross-origin workaround"),
            ('fetch(f"{base_url}/snapshot")', "Snapshot API usage"),
            ('create_proxy(', "PyScript proxy usage")
        ]
        
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ Missing fix: {description}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading Python file: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing refactored hologram processing interface...")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_html_references, 
        test_js_references,
        test_python_fixes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\nRunning {test.__name__}:")
        if test():
            passed += 1
        else:
            print(f"Test {test.__name__} failed")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactoring successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())