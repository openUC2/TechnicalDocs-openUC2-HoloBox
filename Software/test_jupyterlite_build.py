#!/usr/bin/env python3
"""
Test script for JupyterLite build system.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the Software directory to path to import build_jupyter
sys.path.insert(0, str(Path(__file__).parent))

from build_jupyter import JupyterLiteBuilder

def test_build_system():
    """Test the JupyterLite build system."""
    print("Testing JupyterLite build system...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test builder creation
        builder = JupyterLiteBuilder(temp_path / "build")
        
        # Test build process
        success = builder.build()
        
        if success:
            print("✅ Build successful!")
            
            # Check if files were created
            expected_files = [
                "build/_output/lab/index.html"
            ]
            
            all_exist = True
            for file_path in expected_files:
                full_path = temp_path / file_path
                if full_path.exists():
                    print(f"✅ {file_path} exists")
                else:
                    print(f"❌ {file_path} missing")
                    all_exist = False
            
            if all_exist:
                print("✅ All expected files created")
                return True
            else:
                print("❌ Some files missing")
                return False
        else:
            print("❌ Build failed")
            return False

def test_cli_help():
    """Test CLI help functionality."""
    print("\nTesting CLI help...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / "build_jupyter.py"), 
            "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Build JupyterLite for HoloBox" in result.stdout:
            print("✅ CLI help works")
            return True
        else:
            print("❌ CLI help failed")
            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("JupyterLite Build System Tests")
    print("=" * 40)
    
    tests = [
        test_build_system,
        test_cli_help
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())