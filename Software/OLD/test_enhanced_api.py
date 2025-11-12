#!/usr/bin/env python3
"""
Basic test for the enhanced camera API
Tests the new endpoints and functionality
"""

import requests
import json
import time
import sys

# Test configuration
API_BASE = "http://localhost:80"
if len(sys.argv) > 1:
    API_BASE = sys.argv[1]

print(f"Testing HoloBox Camera API at: {API_BASE}")

def test_endpoint(method, path, data=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{API_BASE}{path}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        if response.status_code == expected_status:
            print(f"✅ {method} {path} - Status: {response.status_code}")
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {method} {path} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {path} - Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("HoloBox Camera API Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test basic endpoints
    test_cases = [
        # Basic endpoints
        ("GET", "/", 301),  # Should redirect
        ("GET", "/api/camera/status", 200),
        ("GET", "/settings", 200),
        
        # Stream endpoints (these may fail without camera)
        ("GET", "/stream", 200),
        ("GET", "/api/stream.mjpg", 200),
        ("GET", "/snapshot", 200),
        
        # Camera control endpoints
        ("POST", "/api/camera/exposure_mode", {"auto": True}, 200),
        ("POST", "/api/camera/exposure_mode", {"auto": False}, 200),
        ("POST", "/api/camera/awb_mode", {"auto": True}, 200),
        ("POST", "/api/camera/awb_mode", {"auto": False}, 200),
        ("POST", "/api/camera/resolution", {"width": 800, "height": 600}, 200),
        ("POST", "/api/camera/color", {"mode": "rgb"}, 200),
        ("POST", "/api/camera/color", {"mode": "gray"}, 200),
        
        # Manual controls (these might fail if auto mode is on)
        ("POST", "/api/camera/exposure", {"exposure_us": 20000, "analogue_gain": 2.0}, 200),
        ("POST", "/api/camera/awb_gains", {"red": 1.8, "blue": 1.6}, 200),
        
        # Error cases
        ("POST", "/api/camera/color", {"mode": "invalid"}, 400),
    ]
    
    print("\nRunning API tests...")
    print("-" * 40)
    
    for method, path, *args in test_cases:
        total_tests += 1
        data = args[0] if len(args) > 1 and isinstance(args[0], dict) else None
        expected_status = args[-1] if args else 200
        
        if test_endpoint(method, path, data, expected_status):
            tests_passed += 1
        
        time.sleep(0.1)  # Small delay between tests
    
    # Test WiFi endpoints (may fail in non-Pi environment)
    print("\nTesting WiFi endpoints (may fail outside Pi environment)...")
    print("-" * 40)
    
    wifi_tests = [
        ("GET", "/wifi/status", 200),
        ("GET", "/wifi/scan", 200),
    ]
    
    for method, path, expected_status in wifi_tests:
        total_tests += 1
        if test_endpoint(method, path, None, expected_status):
            tests_passed += 1
        time.sleep(0.1)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} passed")
    
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Overall: PASS (≥80% success rate)")
        return 0
    else:
        print("❌ Overall: FAIL (<80% success rate)")
        return 1

if __name__ == "__main__":
    exit(main())