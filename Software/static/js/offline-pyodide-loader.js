/**
 * Offline Pyodide Package Loader
 * This module helps load Python packages from local files instead of CDN
 */

class OfflinePyodideLoader {
    constructor() {
        this.manifestPath = './js/pyodide-packages/manifest.json';
        this.packagesPath = './js/pyodide-packages/';
        this.manifest = null;
    }
    
    async loadManifest() {
        try {
            const response = await fetch(this.manifestPath);
            this.manifest = await response.json();
            console.log(`📦 Offline packages manifest loaded (${this.manifest.packages.length} packages available)`);
            return true;
        } catch (error) {
            console.warn('⚠️ Could not load offline packages manifest:', error);
            return false;
        }
    }
    
    async setupPyodide() {
        const manifestLoaded = await this.loadManifest();
        
        if (manifestLoaded && this.manifest) {
            // Configure Pyodide to use local packages
            window.pyodideConfig = {
                indexURL: this.packagesPath,
                packageCachePrefix: this.packagesPath,
                packages: this.manifest.packages
            };
            
            console.log(`🐍 Pyodide configured for offline use with packages:`, this.manifest.packages.join(', '));
            return true;
        } else {
            console.log('🌐 Falling back to online package loading');
            return false;
        }
    }
    
    isPackageAvailable(packageName) {
        return this.manifest && this.manifest.packages.includes(packageName);
    }
}

// Initialize the offline loader
window.offlinePyodideLoader = new OfflinePyodideLoader();

// Setup Pyodide when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    await window.offlinePyodideLoader.setupPyodide();
});
