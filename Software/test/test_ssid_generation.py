#!/usr/bin/env python3
"""
Test script for HoloBox SSID generation functionality
"""

import sys
import os
import subprocess
import tempfile

def test_ssid_generator():
    """Test the SSID generator script"""
    print("=== Testing SSID Generator ===")
    
    script_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/generate_ssid.py"
    
    # Check if script exists and is executable
    if not os.path.exists(script_path):
        print("❌ SSID generator script not found")
        return False
    
    if not os.access(script_path, os.X_OK):
        print("❌ SSID generator script not executable")
        return False
    
    # Test script execution
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"❌ SSID generator failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
        
        output_lines = result.stdout.strip().split('\n')
        if len(output_lines) < 3:
            print("❌ SSID generator output incomplete")
            return False
        
        # Extract SSID from output
        ssid_line = output_lines[-1]  # Last line should be "Generated SSID: openUC2-XXX-YYY"
        if not ssid_line.startswith("Generated SSID: openUC2-"):
            print(f"❌ Invalid SSID format: {ssid_line}")
            return False
        
        ssid = ssid_line.split(": ")[1]
        parts = ssid.split("-")
        if len(parts) != 3 or parts[0] != "openUC2":
            print(f"❌ SSID format incorrect: {ssid}")
            return False
        
        print(f"✅ SSID generator working: {ssid}")
        return True
    
    except Exception as e:
        print(f"❌ SSID generator error: {e}")
        return False

def test_access_point_script_updated():
    """Test that access point script uses new SSID generation"""
    print("\n=== Testing Updated Access Point Script ===")
    
    script_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/setup_access_point.sh"
    
    if not os.path.exists(script_path):
        print("❌ Access Point script not found")
        return False
    
    # Check script content for new SSID generation logic
    with open(script_path, 'r') as f:
        content = f.read()
    
    required_components = [
        "generate_ssid.py",
        "openUC2-",
        "cut -d' ' -f3",
        "SCRIPT_DIR=",
        "python3"
    ]
    
    for component in required_components:
        if component in content:
            print(f"✅ Found: {component}")
        else:
            print(f"❌ Missing: {component}")
            return False
    
    # Check that old HoloBox SSID format is removed or fallback only
    if content.count("HoloBox-") > 0:
        print("⚠️  Warning: HoloBox SSID format still present (should be fallback only)")
    
    return True

def test_github_workflow_updated():
    """Test that GitHub workflow includes SSID generator"""
    print("\n=== Testing GitHub Workflow Update ===")
    
    workflow_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/.github/workflows/build-sd-image.yml"
    
    if not os.path.exists(workflow_path):
        print("❌ GitHub workflow file not found")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    required_components = [
        "generate_ssid.py",
        "openUC2-",
        "ADJECTIVES",
        "NOUNS",
        "mac_to_indices",
        "SSIDGEN"
    ]
    
    for component in required_components:
        if component in content:
            print(f"✅ Found in workflow: {component}")
        else:
            print(f"❌ Missing in workflow: {component}")
            return False
    
    return True

def test_ssid_consistency():
    """Test that SSID generation is consistent for same MAC"""
    print("\n=== Testing SSID Consistency ===")
    
    script_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/generate_ssid.py"
    
    if not os.path.exists(script_path):
        print("❌ SSID generator script not found")
        return False
    
    # Run generator multiple times and check consistency
    ssids = []
    for i in range(3):
        try:
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print(f"❌ SSID generator failed on run {i+1}")
                return False
            
            output_lines = result.stdout.strip().split('\n')
            ssid = output_lines[-1].split(": ")[1]
            ssids.append(ssid)
        except Exception as e:
            print(f"❌ Error on run {i+1}: {e}")
            return False
    
    # Check that all SSIDs are the same
    if len(set(ssids)) != 1:
        print(f"❌ SSID generation inconsistent: {ssids}")
        return False
    
    print(f"✅ SSID generation consistent: {ssids[0]}")
    return True

def main():
    """Run all tests"""
    print("HoloBox SSID Generation Tests")
    print("=" * 40)
    
    tests = [
        ("SSID Generator", test_ssid_generator),
        ("Access Point Script", test_access_point_script_updated),
        ("GitHub Workflow", test_github_workflow_updated),
        ("SSID Consistency", test_ssid_consistency)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n=== Test Results: {passed}/{total} passed ===")
    
    if passed == total:
        print("🎉 All tests passed! SSID generation functionality is ready.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)