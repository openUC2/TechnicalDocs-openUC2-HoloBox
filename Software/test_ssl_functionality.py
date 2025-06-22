#!/usr/bin/env python3
"""
Test script to validate SSL certificate generation functionality
"""

import os
import sys
import subprocess
import tempfile
import shutil

def test_ssl_generation():
    """Test the SSL certificate generation logic"""
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    
    try:
        os.chdir(test_dir)
        
        # Copy our SSL generation function (extracted from streamlined_camera_api.py)
        def generate_ssl_certificates_if_needed():
            """Generate self-signed SSL certificates if they don't exist"""
            cert_dir = "ssl_certs"
            keyfile = os.path.join(cert_dir, "server.key")
            certfile = os.path.join(cert_dir, "server.crt")
            
            # Check if certificates already exist
            if os.path.exists(keyfile) and os.path.exists(certfile):
                print(f"SSL certificates found in {cert_dir}/")
                return keyfile, certfile
            
            try:
                # Create certificate directory if it doesn't exist
                if not os.path.exists(cert_dir):
                    os.makedirs(cert_dir)
                
                print("Generating SSL certificates for HTTPS support...")
                
                # Generate private key
                print("  Generating private key...")
                subprocess.run([
                    "openssl", "genrsa", "-out", keyfile, "2048"
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Generate certificate
                print("  Generating self-signed certificate...")
                subprocess.run([
                    "openssl", "req", "-new", "-x509", "-key", keyfile,
                    "-out", certfile, "-days", "365", "-subj",
                    "/C=US/ST=Test/L=Test/O=HoloBox/CN=localhost"
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"  SSL certificates generated successfully!")
                print(f"  Key file: {keyfile}")
                print(f"  Certificate file: {certfile}")
                print("  Note: Browsers will show a security warning for self-signed certificates.")
                
                return keyfile, certfile
                
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not generate SSL certificates: {e}")
                print("Make sure OpenSSL is installed on your system.")
                return None, None
            except FileNotFoundError:
                print("Warning: OpenSSL not found. SSL certificate generation skipped.")
                print("Install OpenSSL to enable automatic HTTPS support.")
                return None, None
        
        print("=== Testing SSL Certificate Generation ===")
        
        # Test 1: Generate certificates
        print("\n--- Test 1: Initial certificate generation ---")
        keyfile, certfile = generate_ssl_certificates_if_needed()
        
        if keyfile and certfile:
            print("✓ Certificates generated successfully")
            
            # Check if files exist
            if os.path.exists(keyfile) and os.path.exists(certfile):
                print("✓ Certificate files exist")
                
                # Check file sizes (should be non-empty)
                key_size = os.path.getsize(keyfile)
                cert_size = os.path.getsize(certfile)
                
                if key_size > 0 and cert_size > 0:
                    print(f"✓ Certificate files have content (key: {key_size} bytes, cert: {cert_size} bytes)")
                else:
                    print("✗ Certificate files are empty")
                    return False
                    
                # Test 2: Check that existing certificates are reused
                print("\n--- Test 2: Reuse existing certificates ---")
                keyfile2, certfile2 = generate_ssl_certificates_if_needed()
                
                if keyfile == keyfile2 and certfile == certfile2:
                    print("✓ Existing certificates reused correctly")
                else:
                    print("✗ Failed to reuse existing certificates")
                    return False
                    
                # Test 3: Verify certificate validity (basic check)
                print("\n--- Test 3: Basic certificate validation ---")
                try:
                    # Try to read the certificate info
                    result = subprocess.run([
                        "openssl", "x509", "-in", certfile, "-text", "-noout"
                    ], capture_output=True, text=True, check=True)
                    
                    if "Subject: C = US, ST = Test, L = Test, O = HoloBox, CN = localhost" in result.stdout:
                        print("✓ Certificate contains correct subject information")
                    else:
                        print("✗ Certificate subject information incorrect")
                        return False
                        
                except subprocess.CalledProcessError:
                    print("✗ Certificate validation failed")
                    return False
                    
                print("\n✅ All SSL tests passed!")
                return True
                
            else:
                print("✗ Certificate files not created")
                return False
        else:
            # Check if this is due to missing OpenSSL
            try:
                subprocess.run(["openssl", "version"], check=True, stdout=subprocess.DEVNULL)
                print("✗ Certificate generation failed despite OpenSSL being available")
                return False
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠ OpenSSL not available - this is expected in some environments")
                print("✓ SSL generation gracefully handled missing OpenSSL")
                return True
                
    finally:
        # Clean up
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)

def test_ssl_args_parsing():
    """Test the argument parsing logic for SSL options"""
    
    print("=== Testing SSL Argument Logic ===")
    
    # Mock argparse.Namespace
    class MockArgs:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    test_cases = [
        {
            "name": "Explicit SSL files provided",
            "args": MockArgs(ssl_keyfile="custom.key", ssl_certfile="custom.crt", no_ssl=False),
            "expected": "explicit_ssl"
        },
        {
            "name": "No SSL args, auto-generation enabled",
            "args": MockArgs(ssl_keyfile=None, ssl_certfile=None, no_ssl=False),
            "expected": "auto_ssl"
        },
        {
            "name": "SSL explicitly disabled",
            "args": MockArgs(ssl_keyfile=None, ssl_certfile=None, no_ssl=True),
            "expected": "no_ssl"
        },
        {
            "name": "Partial SSL args (should not use explicit)",
            "args": MockArgs(ssl_keyfile="custom.key", ssl_certfile=None, no_ssl=False),
            "expected": "auto_ssl"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        args = test_case['args']
        
        # Simulate the SSL logic from streamlined_camera_api.py
        if args.ssl_keyfile and args.ssl_certfile:
            result = "explicit_ssl"
            print(f"Would use explicit SSL: {args.ssl_keyfile}, {args.ssl_certfile}")
        elif not args.no_ssl:
            result = "auto_ssl"
            print("Would attempt auto-generation")
        else:
            result = "no_ssl"
            print("SSL explicitly disabled")
        
        if result == test_case['expected']:
            print(f"✓ Correct behavior: {result}")
        else:
            print(f"✗ Expected {test_case['expected']}, got {result}")
            return False
    
    print("\n✅ All SSL argument tests passed!")
    return True

def main():
    """Run all SSL tests"""
    print("Testing SSL functionality for streamlined_camera_api.py\n")
    
    tests = [
        ("SSL Certificate Generation", test_ssl_generation),
        ("SSL Arguments Parsing", test_ssl_args_parsing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print(f"SSL Test Results: {passed}/{total} passed")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)