#!/usr/bin/env python3
"""
Test script for HoloBox autostart and WiFi functionality
"""

import sys
import os
import subprocess

def test_service_file():
    """Test the service registration functionality"""
    print("=== Testing Service Registration ===")
    
    script_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/registerservice.sh"
    
    # Check if script exists and is executable
    if not os.path.exists(script_path):
        print("❌ Service registration script not found")
        return False
    
    if not os.access(script_path, os.X_OK):
        print("❌ Service registration script not executable")
        return False
    
    # Read the script content to verify it references correct files
    with open(script_path, 'r') as f:
        content = f.read()
    
    if "holobox-camera.service" in content:
        print("✅ Service registration script updated correctly")
    else:
        print("❌ Service registration script not updated")
        return False
    
    if "streamlined_camera_api.py" in content:
        print("✅ Service points to correct Python file")
    else:
        print("❌ Service doesn't point to streamlined_camera_api.py")
        return False
    
    return True

def test_access_point_script():
    """Test the access point setup script"""
    print("\n=== Testing Access Point Script ===")
    
    script_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/setup_access_point.sh"
    
    if not os.path.exists(script_path):
        print("❌ Access Point script not found")
        return False
    
    if not os.access(script_path, os.X_OK):
        print("❌ Access Point script not executable")
        return False
    
    # Check script content for key components
    with open(script_path, 'r') as f:
        content = f.read()
    
    required_components = [
        "hostapd",
        "dnsmasq", 
        "SSID=",
        "192.168.4.1",
        "systemctl enable hostapd"
    ]
    
    for component in required_components:
        if component in content:
            print(f"✅ Found: {component}")
        else:
            print(f"❌ Missing: {component}")
            return False
    
    return True

def test_wifi_client_script():
    """Test the WiFi client setup script"""
    print("\n=== Testing WiFi Client Script ===")
    
    script_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/setup_wifi_client.sh"
    
    if not os.path.exists(script_path):
        print("❌ WiFi client script not found")
        return False
    
    if not os.access(script_path, os.X_OK):
        print("❌ WiFi client script not executable")
        return False
    
    # Check script content
    with open(script_path, 'r') as f:
        content = f.read()
    
    required_components = [
        "--ssid",
        "--password",
        "wpa_supplicant",
        "systemctl stop hostapd"
    ]
    
    for component in required_components:
        if component in content:
            print(f"✅ Found: {component}")
        else:
            print(f"❌ Missing: {component}")
            return False
    
    return True

def test_api_endpoints():
    """Test that WiFi endpoints are added to the API"""
    print("\n=== Testing API WiFi Endpoints ===")
    
    api_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/streamlined_camera_api.py"
    
    with open(api_path, 'r') as f:
        content = f.read()
    
    required_endpoints = [
        "/wifi/status",
        "/wifi/scan", 
        "/wifi/connect",
        "/wifi/access_point"
    ]
    
    for endpoint in required_endpoints:
        if f'"{endpoint}"' in content:
            print(f"✅ Found endpoint: {endpoint}")
        else:
            print(f"❌ Missing endpoint: {endpoint}")
            return False
    
    # Check for WiFiConfig model
    if "class WiFiConfig" in content:
        print("✅ WiFiConfig model found")
    else:
        print("❌ WiFiConfig model missing")
        return False
    
    return True

def test_web_interface():
    """Test that WiFi management is added to web interface"""
    print("\n=== Testing Web Interface ===")
    
    html_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/static/index.html"
    js_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/static/camera_controls.js"
    
    # Check HTML
    with open(html_path, 'r') as f:
        html_content = f.read()
    
    html_elements = [
        "WiFi Management",
        "refreshStatus",
        "scanNetworks",
        "enableAP",
        "connectWifi"
    ]
    
    for element in html_elements:
        if element in html_content:
            print(f"✅ HTML element found: {element}")
        else:
            print(f"❌ HTML element missing: {element}")
            return False
    
    # Check JavaScript
    with open(js_path, 'r') as f:
        js_content = f.read()
    
    js_functions = [
        "refreshWifiStatus",
        "scanNetworks",
        "enableAccessPoint",
        "connectToWifi"
    ]
    
    for func in js_functions:
        if func in js_content:
            print(f"✅ JS function found: {func}")
        else:
            print(f"❌ JS function missing: {func}")
            return False
    
    return True

def test_setup_script():
    """Test the complete setup script"""
    print("\n=== Testing Setup Script ===")
    
    script_path = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/setup_holobox.sh"
    
    if not os.path.exists(script_path):
        print("❌ Setup script not found")
        return False
    
    if not os.access(script_path, os.X_OK):
        print("❌ Setup script not executable")
        return False
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    required_components = [
        "INSTALL_DIR=\"/opt/holobox\"",
        "python3 -m venv",
        "holobox-camera.service",
        "systemctl enable",
        "holobox-info"
    ]
    
    for component in required_components:
        if component in content:
            print(f"✅ Found: {component}")
        else:
            print(f"❌ Missing: {component}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("HoloBox Autostart and WiFi Functionality Tests")
    print("=" * 50)
    
    tests = [
        ("Service Registration", test_service_file),
        ("Access Point Script", test_access_point_script),
        ("WiFi Client Script", test_wifi_client_script),
        ("API Endpoints", test_api_endpoints),
        ("Web Interface", test_web_interface),
        ("Setup Script", test_setup_script)
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
        print("🎉 All tests passed! HoloBox autostart and WiFi functionality is ready.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)