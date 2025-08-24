/* Minimal PyScript JavaScript for HoloBox offline use */

// Basic PyScript functionality for offline use
(function() {
    'use strict';
    
    // Basic polyfill for PyScript functionality
    if (typeof window.PyScript === 'undefined') {
        window.PyScript = {
            init: function() {
                console.log('PyScript offline mode initialized');
            }
        };
    }
    
    // Create py-config element handler
    function handlePyConfig() {
        const pyConfigElements = document.querySelectorAll('py-config');
        pyConfigElements.forEach(element => {
            console.log('Found py-config element, processing packages...');
            // In a full implementation, this would install packages
            // For offline mode, we assume numpy/scipy are available via a different mechanism
        });
    }
    
    // Create py-script element handler
    function handlePyScript() {
        const pyScriptElements = document.querySelectorAll('py-script');
        pyScriptElements.forEach(element => {
            console.log('Found py-script element');
            if (element.hasAttribute('src')) {
                const src = element.getAttribute('src');
                console.log('PyScript source file:', src);
                // In offline mode, the Python script should be loaded separately
                // This is a placeholder that indicates the script would be processed
            } else {
                console.log('Inline PyScript code found');
                // Inline code would be processed here
            }
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            handlePyConfig();
            handlePyScript();
            window.PyScript.init();
        });
    } else {
        handlePyConfig();
        handlePyScript();
        window.PyScript.init();
    }
    
    // Basic error handling
    window.addEventListener('error', function(e) {
        console.warn('PyScript offline error:', e.message);
    });
    
    console.log('PyScript offline compatibility layer loaded');
    
})();