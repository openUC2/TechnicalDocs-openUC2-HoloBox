#!/usr/bin/env python3
"""
Test script to simulate server startup with SSL functionality
"""

import os
import sys
import subprocess
import tempfile
import shutil
import argparse

def simulate_ssl_startup():
    """Simulate the SSL startup logic from streamlined_camera_api.py"""
    
    # Extract the SSL generation function
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

    # Simulate argument parsing like in streamlined_camera_api.py
    parser = argparse.ArgumentParser(description="Streamlined Camera API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind to")
    parser.add_argument("--ssl-keyfile", help="SSL private key file")
    parser.add_argument("--ssl-certfile", help="SSL certificate file")
    parser.add_argument("--no-ssl", action="store_true", help="Disable automatic SSL certificate generation")
    
    # Test different argument combinations
    test_scenarios = [
        {
            "name": "Default behavior (auto-SSL)",
            "args": []
        },
        {
            "name": "Explicit SSL files",
            "args": ["--ssl-keyfile", "custom.key", "--ssl-certfile", "custom.crt"]
        },
        {
            "name": "SSL disabled",
            "args": ["--no-ssl"]
        },
        {
            "name": "Custom host and port with auto-SSL",
            "args": ["--host", "localhost", "--port", "8443"]
        }
    ]
    
    print("=== Testing Server SSL Startup Scenarios ===\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- Scenario {i}: {scenario['name']} ---")
        
        # Parse arguments
        args = parser.parse_args(scenario['args'])
        print(f"Arguments: {scenario['args']}")
        
        # Simulate the SSL configuration logic
        ssl_kwargs = {}
        
        # If SSL files are explicitly provided, use them
        if args.ssl_keyfile and args.ssl_certfile:
            ssl_kwargs = {
                "ssl_keyfile": args.ssl_keyfile,
                "ssl_certfile": args.ssl_certfile
            }
            print(f"Starting server with SSL on https://{args.host}:{args.port}")
            print(f"Using provided certificates: {args.ssl_keyfile}, {args.ssl_certfile}")
        
        # If no SSL files provided and SSL not disabled, try to auto-generate
        elif not args.no_ssl:
            auto_keyfile, auto_certfile = generate_ssl_certificates_if_needed()
            if auto_keyfile and auto_certfile:
                ssl_kwargs = {
                    "ssl_keyfile": auto_keyfile,
                    "ssl_certfile": auto_certfile
                }
                print(f"Starting server with auto-generated SSL on https://{args.host}:{args.port}")
            else:
                print(f"Starting server without SSL on http://{args.host}:{args.port}")
                print("SSL certificate generation failed. Running in HTTP mode.")
        
        # SSL explicitly disabled
        else:
            print(f"Starting server without SSL on http://{args.host}:{args.port}")
            print("SSL disabled by --no-ssl flag")
        
        # Show SSL usage information
        if not ssl_kwargs:
            print("For manual SSL support, use --ssl-keyfile and --ssl-certfile arguments")
            print("To disable automatic SSL generation, use --no-ssl")
        
        # Don't actually start uvicorn, just show what would happen
        print(f"Would call: uvicorn.run(app, host='{args.host}', port={args.port}, **{ssl_kwargs})")
        
        print("✅ Scenario completed successfully\n")
    
    return True

def main():
    """Test server SSL startup in a clean environment"""
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    
    try:
        os.chdir(test_dir)
        print(f"Testing in temporary directory: {test_dir}\n")
        
        return simulate_ssl_startup()
        
    finally:
        # Clean up
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)