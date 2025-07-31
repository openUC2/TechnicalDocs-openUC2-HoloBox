#!/usr/bin/env python3
"""
Test script to validate the SD card image build system
"""

import os
import subprocess
import sys
from pathlib import Path

def test_file_exists(file_path, description):
    """Test if a file exists and is readable"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ {description}: File not found - {file_path}")
        return False
    
    if not path.is_file():
        print(f"❌ {description}: Not a file - {file_path}")
        return False
    
    print(f"✅ {description}: Found")
    return True

def test_file_executable(file_path, description):
    """Test if a file exists and is executable"""
    if not test_file_exists(file_path, description):
        return False
    
    if not os.access(file_path, os.X_OK):
        print(f"❌ {description}: Not executable - {file_path}")
        return False
    
    print(f"✅ {description}: Executable")
    return True

def test_directory_exists(dir_path, description):
    """Test if a directory exists"""
    path = Path(dir_path)
    if not path.exists():
        print(f"❌ {description}: Directory not found - {dir_path}")
        return False
    
    if not path.is_dir():
        print(f"❌ {description}: Not a directory - {dir_path}")
        return False
    
    print(f"✅ {description}: Found")
    return True

def test_yaml_syntax(yaml_file):
    """Test YAML file syntax"""
    try:
        import yaml
        with open(yaml_file, 'r') as f:
            yaml.safe_load(f)
        print(f"✅ GitHub Actions workflow: Valid YAML syntax")
        return True
    except ImportError:
        print(f"⚠️ GitHub Actions workflow: Cannot validate YAML (PyYAML not installed)")
        return True  # Don't fail if PyYAML is not available
    except Exception as e:
        print(f"❌ GitHub Actions workflow: Invalid YAML - {e}")
        return False

def test_script_content(script_path, required_content, description):
    """Test if script contains required content"""
    try:
        with open(script_path, 'r') as f:
            content = f.read()
        
        missing = []
        for item in required_content:
            if item not in content:
                missing.append(item)
        
        if missing:
            print(f"❌ {description}: Missing required content: {missing}")
            return False
        
        print(f"✅ {description}: All required content found")
        return True
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing HoloBox SD Card Image Build System")
    print("=" * 50)
    
    # Get repository root
    repo_root = Path(__file__).parent.parent
    
    tests_passed = 0
    tests_total = 0
    
    # Test GitHub Actions workflow
    tests_total += 1
    workflow_file = repo_root / ".github" / "workflows" / "build-sd-image.yml"
    if test_file_exists(workflow_file, "GitHub Actions workflow file"):
        if test_yaml_syntax(workflow_file):
            tests_passed += 1
    
    # Test build scripts
    tests_total += 1
    build_script = repo_root / "Scripts" / "build_sd_image.sh"
    if test_file_executable(build_script, "Local build script"):
        tests_passed += 1
    
    tests_total += 1
    setup_script = repo_root / "Software" / "setup_holobox_image.sh"
    if test_file_executable(setup_script, "Image setup script"):
        tests_passed += 1
    
    # Test original setup script
    tests_total += 1
    original_setup = repo_root / "Software" / "setup_holobox.sh"
    if test_file_executable(original_setup, "Original setup script"):
        tests_passed += 1
    
    # Test required directories
    tests_total += 1
    if test_directory_exists(repo_root / "Software", "Software directory"):
        tests_passed += 1
    
    tests_total += 1
    if test_directory_exists(repo_root / ".github" / "workflows", "GitHub workflows directory"):
        tests_passed += 1
    
    # Test GitHub Actions workflow content
    tests_total += 1
    required_workflow_content = [
        "qemu-user-static",
        "raspios_lite_arm64",
        "chroot",
        "softprops/action-gh-release",
        "holobox-sdcard-"
    ]
    if test_script_content(workflow_file, required_workflow_content, "GitHub Actions workflow content"):
        tests_passed += 1
    
    # Test setup script content
    tests_total += 1
    required_setup_content = [
        "python3 -m venv",
        "systemctl enable",
        "holobox-camera.service",
        "/opt/holobox"
    ]
    if test_script_content(setup_script, required_setup_content, "Setup script content"):
        tests_passed += 1
    
    # Test Python requirements
    tests_total += 1
    requirements_file = repo_root / "Software" / "requirements.txt"
    if test_file_exists(requirements_file, "Python requirements file"):
        required_packages = ["fastapi", "uvicorn", "numpy", "opencv-python-headless"]
        if test_script_content(requirements_file, required_packages, "Python requirements content"):
            tests_passed += 1
    
    # Test core software files
    core_files = [
        ("Software/streamlined_camera_api.py", "Camera API server"),
        ("Software/setup_access_point.sh", "Access Point setup script"),
        ("Software/setup_wifi_client.sh", "WiFi client setup script"),
        ("Scripts/README.md", "Build system documentation")
    ]
    
    for file_path, description in core_files:
        tests_total += 1
        full_path = repo_root / file_path
        if test_file_exists(full_path, description):
            tests_passed += 1
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! The SD card image build system is ready.")
        return 0
    else:
        print(f"❌ {tests_total - tests_passed} tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)