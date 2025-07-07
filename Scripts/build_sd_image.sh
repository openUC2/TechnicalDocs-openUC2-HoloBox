#!/bin/bash
# Local build script for testing HoloBox SD card image creation
# This script can be used to build the image locally for testing

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="/tmp/holobox-build"
IMAGE_NAME="holobox-sdcard-$(date +%Y%m%d).img"
LOOP_DEVICE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

cleanup() {
    log "Cleaning up..."
    
    # Unmount everything if mounted
    if [ -n "$LOOP_DEVICE" ]; then
        sudo umount ${LOOP_DEVICE}p1 2>/dev/null || true
        sudo umount ${LOOP_DEVICE}p2 2>/dev/null || true
        sudo losetup -d "$LOOP_DEVICE" 2>/dev/null || true
    fi
    
    # Unmount any remaining mount points
    sudo umount "$BUILD_DIR/mount/boot" 2>/dev/null || true
    sudo umount "$BUILD_DIR/mount/dev/pts" 2>/dev/null || true
    sudo umount "$BUILD_DIR/mount/dev" 2>/dev/null || true
    sudo umount "$BUILD_DIR/mount/sys" 2>/dev/null || true
    sudo umount "$BUILD_DIR/mount/proc" 2>/dev/null || true
    sudo umount "$BUILD_DIR/mount" 2>/dev/null || true
    
    # Remove build directory
    rm -rf "$BUILD_DIR"
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

check_dependencies() {
    log "Checking dependencies..."
    
    local missing_deps=()
    
    command -v qemu-aarch64-static >/dev/null || missing_deps+=("qemu-user-static")
    command -v parted >/dev/null || missing_deps+=("parted")
    command -v losetup >/dev/null || missing_deps+=("util-linux")
    command -v zip >/dev/null || missing_deps+=("zip")
    command -v wget >/dev/null || missing_deps+=("wget")
    command -v xz >/dev/null || missing_deps+=("xz-utils")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing_deps[*]}\nInstall with: sudo apt-get install qemu-user-static parted util-linux zip wget xz-utils binfmt-support"
    fi
    
    success "All dependencies found"
}

check_permissions() {
    log "Checking permissions..."
    
    if [ "$EUID" -eq 0 ]; then
        error "This script should not be run as root. Use a regular user with sudo access."
    fi
    
    if ! sudo -n true 2>/dev/null; then
        error "This script requires sudo access. Please run with a user that has sudo privileges."
    fi
    
    success "Permissions OK"
}

download_base_image() {
    log "Downloading Raspberry Pi OS Lite 64-bit..."
    
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    
    if [ ! -f "rpi-os-lite.img.xz" ]; then
        wget -O rpi-os-lite.img.xz \
            "https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz"
    else
        log "Base image already downloaded"
    fi
    
    if [ ! -f "rpi-os-lite.img" ]; then
        log "Extracting base image..."
        xz -d rpi-os-lite.img.xz
    else
        log "Base image already extracted"
    fi
    
    success "Base image ready"
}

expand_image() {
    log "Expanding image size..."
    
    cd "$BUILD_DIR"
    
    # Add 2GB to accommodate our software
    dd if=/dev/zero bs=1M count=2048 >> rpi-os-lite.img
    
    # Find available loop device
    LOOP_DEVICE=$(sudo losetup -f)
    sudo losetup -P "$LOOP_DEVICE" rpi-os-lite.img
    
    log "Using loop device: $LOOP_DEVICE"
    
    # Expand the partition
    sudo parted "$LOOP_DEVICE" resizepart 2 100%
    sudo e2fsck -f "${LOOP_DEVICE}p2"
    sudo resize2fs "${LOOP_DEVICE}p2"
    
    success "Image expanded"
}

setup_chroot() {
    log "Setting up chroot environment..."
    
    mkdir -p "$BUILD_DIR/mount"
    
    # Mount the partitions
    sudo mount "${LOOP_DEVICE}p2" "$BUILD_DIR/mount"
    sudo mount "${LOOP_DEVICE}p1" "$BUILD_DIR/mount/boot"
    
    # Setup chroot environment
    sudo cp /usr/bin/qemu-aarch64-static "$BUILD_DIR/mount/usr/bin/"
    
    # Mount proc, sys, dev for chroot
    sudo mount -t proc proc "$BUILD_DIR/mount/proc"
    sudo mount -t sysfs sysfs "$BUILD_DIR/mount/sys"
    sudo mount --bind /dev "$BUILD_DIR/mount/dev"
    sudo mount --bind /dev/pts "$BUILD_DIR/mount/dev/pts"
    
    # Copy our software into the image
    sudo mkdir -p "$BUILD_DIR/mount/opt/holobox-install"
    sudo cp -r "$SCRIPT_DIR"/* "$BUILD_DIR/mount/opt/holobox-install/"
    
    success "Chroot environment ready"
}

install_holobox() {
    log "Installing HoloBox software..."
    
    # Use the image-specific setup script
    sudo cp "$SCRIPT_DIR/setup_holobox_image.sh" "$BUILD_DIR/mount/install_holobox.sh"
    sudo chmod +x "$BUILD_DIR/mount/install_holobox.sh"
    
    # Run installation in chroot
    sudo chroot "$BUILD_DIR/mount" /install_holobox.sh
    
    # Clean up installation script
    sudo rm -f "$BUILD_DIR/mount/install_holobox.sh"
    sudo rm -rf "$BUILD_DIR/mount/opt/holobox-install"
    
    success "HoloBox software installed"
}

finalize_image() {
    log "Finalizing image..."
    
    # Clean up package cache
    sudo chroot "$BUILD_DIR/mount" apt-get clean
    sudo chroot "$BUILD_DIR/mount" rm -rf /var/lib/apt/lists/*
    
    # Remove temporary files
    sudo rm -f "$BUILD_DIR/mount/usr/bin/qemu-aarch64-static"
    
    # Sync filesystem
    sudo sync
    
    # Unmount everything
    sudo umount "$BUILD_DIR/mount/dev/pts"
    sudo umount "$BUILD_DIR/mount/dev"
    sudo umount "$BUILD_DIR/mount/sys"
    sudo umount "$BUILD_DIR/mount/proc"
    sudo umount "$BUILD_DIR/mount/boot"
    sudo umount "$BUILD_DIR/mount"
    
    # Detach loop device
    sudo losetup -d "$LOOP_DEVICE"
    LOOP_DEVICE=""
    
    success "Image finalized"
}

compress_image() {
    log "Compressing image..."
    
    cd "$BUILD_DIR"
    
    # Copy to final location with proper name
    cp rpi-os-lite.img "$IMAGE_NAME"
    
    # Compress the image
    zip -9 "${IMAGE_NAME}.zip" "$IMAGE_NAME"
    
    # Get file size
    local size=$(du -h "${IMAGE_NAME}.zip" | cut -f1)
    success "Image compressed: ${IMAGE_NAME}.zip ($size)"
    
    # Move to script directory
    mv "${IMAGE_NAME}.zip" "$SCRIPT_DIR/"
    
    log "Image saved to: $SCRIPT_DIR/${IMAGE_NAME}.zip"
}

main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║         HoloBox SD Image Builder         ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_permissions
    check_dependencies
    download_base_image
    expand_image
    setup_chroot
    install_holobox
    finalize_image
    compress_image
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════╗"
    echo "║             Build Complete!              ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo ""
    echo "🎉 HoloBox SD card image created successfully!"
    echo "📁 Location: $SCRIPT_DIR/${IMAGE_NAME}.zip"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Flash the image to an SD card (8GB+ recommended)"
    echo "   2. Insert into Raspberry Pi and power on"
    echo "   3. Connect to HoloBox-XXXXX WiFi (password: holobox123)"
    echo "   4. Open browser to http://192.168.4.1:8000/static/"
    echo ""
    echo "🔑 Default credentials:"
    echo "   SSH User: pi"
    echo "   SSH Password: holobox123"
    echo ""
}

# Run main function
main "$@"