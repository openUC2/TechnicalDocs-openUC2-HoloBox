/**
 * PyScript Fallback Loader
 * 
 * This script detects whether PyScript/Pyodide can run on the current platform
 * and automatically falls back to a pure JavaScript implementation when needed.
 * 
 * Detection criteria:
 * - iOS/iPadOS devices (known to have issues with PyScript/Pyodide)
 * - WebAssembly support
 * - SharedArrayBuffer support
 * - PyScript initialization timeout
 */

class PyScriptFallbackLoader {
    constructor() {
        this.isPyScriptAvailable = false;
        this.isFallbackMode = false;
        this.pyScriptTimeout = 10000; // 10 seconds timeout for PyScript to initialize
        this.pyScriptInitTimer = null;
        this.fallbackProcessor = null;
        
        console.log("🔍 Initializing PyScript Fallback Loader...");
    }

    /**
     * Detect if the current device is iOS/iPadOS
     */
    isIOSDevice() {
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        
        // Check for iPad, iPhone, or iPod
        const isIOS = /iPad|iPhone|iPod/.test(userAgent);
        
        // Check for iPad Pro with MacIntel user agent (iOS 13+)
        const isIPadPro = navigator.platform === 'MacIntel' && 
                         typeof navigator.maxTouchPoints !== 'undefined' && 
                         navigator.maxTouchPoints > 1;
        
        return isIOS || isIPadPro;
    }

    /**
     * Check if WebAssembly is supported
     */
    isWasmSupported() {
        try {
            if (typeof WebAssembly === 'object' && 
                typeof WebAssembly.instantiate === 'function') {
                const module = new WebAssembly.Module(
                    Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00)
                );
                if (module instanceof WebAssembly.Module) {
                    return true;
                }
            }
        } catch (e) {
            console.warn("⚠️ WebAssembly not supported:", e);
        }
        return false;
    }

    /**
     * Check if SharedArrayBuffer is supported (required for threading in Pyodide)
     */
    isSharedArrayBufferSupported() {
        try {
            return typeof SharedArrayBuffer !== 'undefined';
        } catch (e) {
            return false;
        }
    }

    /**
     * Determine if we should use fallback mode
     */
    shouldUseFallback() {
        const isIOS = this.isIOSDevice();
        const hasWasm = this.isWasmSupported();
        const hasSAB = this.isSharedArrayBufferSupported();
        
        console.log("📊 Platform Detection:");
        console.log(`  - iOS/iPadOS: ${isIOS}`);
        console.log(`  - WebAssembly: ${hasWasm}`);
        console.log(`  - SharedArrayBuffer: ${hasSAB}`);
        
        // Use fallback if on iOS (known issues) or missing critical features
        if (isIOS) {
            console.log("⚠️ iOS/iPadOS detected - PyScript/Pyodide may not work reliably");
            return true;
        }
        
        if (!hasWasm) {
            console.log("⚠️ WebAssembly not supported - fallback required");
            return true;
        }
        
        // Note: SharedArrayBuffer is not strictly required for basic Pyodide,
        // but its absence may indicate other limitations
        if (!hasSAB) {
            console.log("⚠️ SharedArrayBuffer not supported - may affect performance");
        }
        
        return false;
    }

    /**
     * Show a notification to the user about fallback mode
     */
    showFallbackNotification() {
        // Create notification element
        const notification = document.createElement('div');
        notification.id = 'pyscript-fallback-notification';
        notification.style.cssText = `
            position: fixed;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            max-width: 90%;
            width: 600px;
            font-family: system-ui, -apple-system, sans-serif;
            animation: slideDown 0.5s ease-out;
        `;
        
        const isOffAxis = window.location.href.includes('offaxis');
        const warningMessage = isOffAxis 
            ? 'Off-axis holographic reconstruction requires full FFT processing and is not available in fallback mode.'
            : 'Using simplified JavaScript processing without full holographic reconstruction.';
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 28px;">📱</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 5px;">
                        JavaScript Fallback Mode Active
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.95;">
                        PyScript is not available on this device. ${warningMessage}
                    </div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: rgba(255,255,255,0.2); border: none; color: white; 
                               padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 0.9em;">
                    Dismiss
                </button>
            </div>
        `;
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateX(-50%) translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 15 seconds (longer for important message)
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideDown 0.5s ease-out reverse';
                setTimeout(() => notification.remove(), 500);
            }
        }, 15000);
    }

    /**
     * Update status indicators in the UI
     */
    updateStatusIndicators() {
        const statusElem = document.getElementById('status');
        if (statusElem && this.isFallbackMode) {
            statusElem.innerHTML = 'Ready (JavaScript Fallback Mode) - Click Start Stream to begin';
        }
        
        // Add a visual indicator to the processing status
        const processingStatus = document.querySelector('.processing-status');
        if (processingStatus && this.isFallbackMode) {
            const indicator = document.createElement('div');
            indicator.style.cssText = `
                margin-top: 10px;
                padding: 10px;
                background: rgba(102, 126, 234, 0.1);
                border-left: 3px solid #667eea;
                border-radius: 4px;
            `;
            indicator.innerHTML = `
                <strong>Mode:</strong> JavaScript Fallback<br>
                <small style="opacity: 0.8;">
                    Limited holographic reconstruction without FFT. Full processing requires a compatible device.
                </small>
            `;
            processingStatus.appendChild(indicator);
        }
    }

    /**
     * Initialize the fallback JavaScript processor
     */
    async initializeFallback() {
        console.log("🔄 Initializing JavaScript fallback...");
        
        try {
            // Load the fallback script if not already loaded
            if (typeof window.HologramProcessorFallback === 'undefined') {
                await this.loadScript('./js/hologram_processing_fallback.js');
            }
            
            // Create and initialize the fallback processor
            this.fallbackProcessor = new window.HologramProcessorFallback();
            this.fallbackProcessor.initializeEventListeners();
            
            this.isFallbackMode = true;
            this.showFallbackNotification();
            this.updateStatusIndicators();
            
            console.log("✅ JavaScript fallback initialized successfully");
            return true;
            
        } catch (e) {
            console.error("❌ Failed to initialize fallback:", e);
            return false;
        }
    }

    /**
     * Load a script dynamically
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Monitor PyScript initialization
     */
    monitorPyScriptInit() {
        return new Promise((resolve, reject) => {
            // Set a timeout for PyScript initialization
            this.pyScriptInitTimer = setTimeout(() => {
                console.warn("⏱️ PyScript initialization timeout - switching to fallback");
                reject(new Error("PyScript initialization timeout"));
            }, this.pyScriptTimeout);
            
            // Check if PyScript is available
            const checkInterval = setInterval(() => {
                // Check for various indicators that PyScript has initialized
                if (typeof window.pyscript !== 'undefined' || 
                    typeof window.pyodide !== 'undefined' ||
                    document.querySelector('py-script[src]')?.hasAttribute('data-initialized')) {
                    
                    clearTimeout(this.pyScriptInitTimer);
                    clearInterval(checkInterval);
                    this.isPyScriptAvailable = true;
                    console.log("✅ PyScript initialized successfully");
                    resolve(true);
                }
            }, 100);
        });
    }

    /**
     * Main initialization method
     */
    async initialize() {
        console.log("🚀 Starting PyScript/Fallback initialization...");
        
        // Check if we should immediately use fallback
        if (this.shouldUseFallback()) {
            console.log("🔀 Using fallback mode based on platform detection");
            await this.initializeFallback();
            return;
        }
        
        // Otherwise, try to wait for PyScript and fall back if it fails
        console.log("⏳ Waiting for PyScript initialization...");
        
        try {
            await this.monitorPyScriptInit();
            console.log("✅ PyScript is available - using PyScript mode");
        } catch (e) {
            console.warn("⚠️ PyScript failed to initialize:", e);
            console.log("🔀 Switching to JavaScript fallback...");
            await this.initializeFallback();
        }
    }
}

// Initialize the loader when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.pyScriptFallbackLoader = new PyScriptFallbackLoader();
        window.pyScriptFallbackLoader.initialize();
    });
} else {
    // DOM is already ready
    window.pyScriptFallbackLoader = new PyScriptFallbackLoader();
    window.pyScriptFallbackLoader.initialize();
}

// Export for debugging
window.PyScriptFallbackLoader = PyScriptFallbackLoader;
