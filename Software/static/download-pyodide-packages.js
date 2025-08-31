#!/usr/bin/env node

/**
 * Download Pyodide packages for offline use
 * This script downloads numpy, scipy and other packages from the Pyodide CDN
 */

const fs = require('fs');
const path = require('path');

// Use dynamic import for node-fetch (ESM module)
async function downloadPackages() {
    try {
        const { default: fetch } = await import('node-fetch');
        
        // Pyodide version - should match what PyScript uses
        const PYODIDE_VERSION = '0.24.1';
        const PYODIDE_BASE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full`;
        
        // Packages we want to download
        const packages = [
            'numpy',
            'scipy',
            'opencv-python',
            'pillow'
        ];
        
        // Create output directory
        const outputDir = path.join(__dirname, 'js', 'pyodide-packages');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        console.log(`Downloading Pyodide packages to ${outputDir}...`);
        
        // First, get the package index to know what files we need
        console.log('Fetching package index...');
        const indexResponse = await fetch(`${PYODIDE_BASE_URL}/packages.json`);
        const packageIndex = await indexResponse.json();
        
        // Save the package index
        fs.writeFileSync(
            path.join(outputDir, 'packages.json'), 
            JSON.stringify(packageIndex, null, 2)
        );
        
        // Download each package and its dependencies
        const downloadedPackages = new Set();
        
        async function downloadPackage(packageName) {
            if (downloadedPackages.has(packageName)) {
                return;
            }
            
            const packageInfo = packageIndex.packages[packageName];
            if (!packageInfo) {
                console.warn(`Package ${packageName} not found in index`);
                return;
            }
            
            console.log(`Downloading ${packageName}...`);
            
            // Download the package file
            const packageUrl = `${PYODIDE_BASE_URL}/${packageInfo.file_name}`;
            const packageResponse = await fetch(packageUrl);
            
            if (packageResponse.ok) {
                const packageData = await packageResponse.arrayBuffer();
                fs.writeFileSync(
                    path.join(outputDir, packageInfo.file_name),
                    Buffer.from(packageData)
                );
                console.log(`✓ Downloaded ${packageInfo.file_name}`);
                downloadedPackages.add(packageName);
                
                // Download dependencies recursively
                if (packageInfo.depends) {
                    for (const dep of packageInfo.depends) {
                        await downloadPackage(dep);
                    }
                }
            } else {
                console.error(`Failed to download ${packageName}: ${packageResponse.status}`);
            }
        }
        
        // Download all requested packages
        for (const packageName of packages) {
            await downloadPackage(packageName);
        }
        
        // Create a manifest file for easy loading
        const manifest = {
            pyodideVersion: PYODIDE_VERSION,
            baseUrl: PYODIDE_BASE_URL,
            packages: Array.from(downloadedPackages),
            downloadDate: new Date().toISOString()
        };
        
        fs.writeFileSync(
            path.join(outputDir, 'manifest.json'),
            JSON.stringify(manifest, null, 2)
        );
        
        console.log(`\n✅ Successfully downloaded ${downloadedPackages.size} packages:`);
        downloadedPackages.forEach(pkg => console.log(`  - ${pkg}`));
        console.log('\nOffline packages are ready!');
        
    } catch (error) {
        console.error('Error downloading packages:', error);
        process.exit(1);
    }
}

// Run the download
downloadPackages();
