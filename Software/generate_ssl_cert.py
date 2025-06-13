#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for HTTPS testing
"""

import os
import subprocess
import sys

def generate_ssl_cert():
    """Generate self-signed SSL certificate for testing"""
    cert_dir = "ssl_certs"
    
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    keyfile = os.path.join(cert_dir, "server.key")
    certfile = os.path.join(cert_dir, "server.crt")
    
    # Check if certificates already exist
    if os.path.exists(keyfile) and os.path.exists(certfile):
        print(f"SSL certificates already exist in {cert_dir}/")
        print(f"Key file: {keyfile}")
        print(f"Certificate file: {certfile}")
        return keyfile, certfile
    
    # Generate private key
    print("Generating private key...")
    subprocess.run([
        "openssl", "genrsa", "-out", keyfile, "2048"
    ], check=True)
    
    # Generate certificate
    print("Generating self-signed certificate...")
    subprocess.run([
        "openssl", "req", "-new", "-x509", "-key", keyfile,
        "-out", certfile, "-days", "365", "-subj",
        "/C=US/ST=Test/L=Test/O=HoloBox/CN=localhost"
    ], check=True)
    
    print(f"SSL certificates generated successfully!")
    print(f"Key file: {keyfile}")
    print(f"Certificate file: {certfile}")
    print("\nTo start the server with SSL:")
    print(f"python streamlined_camera_api.py --ssl-keyfile {keyfile} --ssl-certfile {certfile}")
    print("\nNote: Browsers will show a security warning for self-signed certificates.")
    print("You can safely ignore this for development/testing purposes.")
    
    return keyfile, certfile

if __name__ == "__main__":
    try:
        generate_ssl_cert()
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {e}")
        print("Make sure OpenSSL is installed on your system.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: OpenSSL not found. Please install OpenSSL to generate certificates.")
        print("On Ubuntu/Debian: sudo apt-get install openssl")
        print("On macOS: brew install openssl")
        sys.exit(1)