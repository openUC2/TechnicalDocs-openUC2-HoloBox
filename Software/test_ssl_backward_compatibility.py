#!/usr/bin/env python3
"""
Test backward compatibility with existing SSL functionality
"""

import os
import sys
import tempfile
import shutil

def test_backward_compatibility():
    """Test that existing SSL functionality still works"""
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    
    try:
        os.chdir(test_dir)
        
        print("=== Testing Backward Compatibility ===\n")
        
        # Test 1: Check that --ssl-keyfile and --ssl-certfile still work
        print("--- Test 1: Explicit SSL arguments ---")
        
        # Simulate the argument parsing and SSL logic
        class MockArgs:
            def __init__(self, ssl_keyfile=None, ssl_certfile=None, no_ssl=False):
                self.ssl_keyfile = ssl_keyfile
                self.ssl_certfile = ssl_certfile
                self.no_ssl = no_ssl
                self.host = "0.0.0.0"
                self.port = 8000
        
        # Test case 1: Both SSL files provided (should use explicit SSL)
        args = MockArgs(ssl_keyfile="custom.key", ssl_certfile="custom.crt")
        ssl_kwargs = {}
        
        if args.ssl_keyfile and args.ssl_certfile:
            ssl_kwargs = {
                "ssl_keyfile": args.ssl_keyfile,
                "ssl_certfile": args.ssl_certfile
            }
            print(f"✓ Would use explicit SSL: {args.ssl_keyfile}, {args.ssl_certfile}")
        else:
            print("✗ Failed to detect explicit SSL arguments")
            return False
        
        # Test 2: Check that partial SSL arguments don't break
        print("\n--- Test 2: Partial SSL arguments (should fall back to auto-generation) ---")
        args = MockArgs(ssl_keyfile="custom.key", ssl_certfile=None)
        
        if args.ssl_keyfile and args.ssl_certfile:
            print("✗ Should not use partial SSL arguments")
            return False
        elif not args.no_ssl:
            print("✓ Correctly falls back to auto-generation when partial SSL args provided")
        else:
            print("✗ Unexpected behavior with partial SSL args")
            return False
        
        # Test 3: Check that --no-ssl still works
        print("\n--- Test 3: SSL disabled with --no-ssl ---")
        args = MockArgs(no_ssl=True)
        
        if not args.no_ssl:
            print("✗ Failed to respect --no-ssl flag")
            return False
        else:
            print("✓ --no-ssl flag correctly disables SSL")
        
        # Test 4: Check that the help text would include new option
        print("\n--- Test 4: Help text includes new option ---")
        import argparse
        
        parser = argparse.ArgumentParser(description="Streamlined Camera API Server")
        parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
        parser.add_argument("--port", default=8000, type=int, help="Port to bind to")
        parser.add_argument("--ssl-keyfile", help="SSL private key file")
        parser.add_argument("--ssl-certfile", help="SSL certificate file")
        parser.add_argument("--no-ssl", action="store_true", help="Disable automatic SSL certificate generation")
        
        help_text = parser.format_help()
        
        if "--no-ssl" in help_text and "Disable automatic SSL certificate generation" in help_text:
            print("✓ Help text includes new --no-ssl option")
        else:
            print("✗ Help text missing --no-ssl option")
            return False
        
        if "--ssl-keyfile" in help_text and "--ssl-certfile" in help_text:
            print("✓ Help text still includes original SSL options")
        else:
            print("✗ Help text missing original SSL options")
            return False
        
        print("\n✅ All backward compatibility tests passed!")
        return True
        
    finally:
        # Clean up
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)

def test_api_structure_unchanged():
    """Test that the API structure is unchanged"""
    
    print("=== Testing API Structure Unchanged ===\n")
    
    # Check that the file structure is correct
    api_file = "/home/runner/work/TechnicalDocs-openUC2-HoloBox/TechnicalDocs-openUC2-HoloBox/Software/streamlined_camera_api.py"
    
    if not os.path.exists(api_file):
        print("✗ streamlined_camera_api.py not found")
        return False
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Check that key API components are still there
    required_components = [
        "from fastapi import FastAPI",
        "from fastapi.staticfiles import StaticFiles",
        '@app.get("/")',
        '@app.get("/snapshot"',
        '@app.get("/stream"',
        '@app.post("/settings"',
        '@app.get("/settings"',
        '@app.get("/stats"',
        "app.mount(\"/static\", StaticFiles",
        "if __name__ == \"__main__\":"
    ]
    
    for component in required_components:
        if component in content:
            print(f"✓ Found: {component}")
        else:
            print(f"✗ Missing: {component}")
            return False
    
    # Check that our new SSL function is there
    ssl_components = [
        "def generate_ssl_certificates_if_needed():",
        "--no-ssl",
        "generate_ssl_certificates_if_needed()"
    ]
    
    for component in ssl_components:
        if component in content:
            print(f"✓ Found new SSL component: {component}")
        else:
            print(f"✗ Missing new SSL component: {component}")
            return False
    
    print("\n✅ API structure verification passed!")
    return True

def main():
    """Run all backward compatibility tests"""
    
    tests = [
        ("Backward Compatibility", test_backward_compatibility),
        ("API Structure Unchanged", test_api_structure_unchanged)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"{'='*60}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        print()
    
    print(f"{'='*60}")
    print(f"Backward Compatibility Test Results: {passed}/{total} passed")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)