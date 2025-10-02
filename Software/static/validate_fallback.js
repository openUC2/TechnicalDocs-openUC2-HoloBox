#!/usr/bin/env node

/**
 * Validation script for PyScript Fallback implementation
 * 
 * This script validates the fallback system without requiring a browser.
 * It checks:
 * - File existence
 * - JavaScript syntax
 * - API compatibility
 * - Code structure
 */

const fs = require('fs');
const path = require('path');

// Color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

function log(message, type = 'info') {
    const colorMap = {
        pass: colors.green,
        fail: colors.red,
        warn: colors.yellow,
        info: colors.cyan
    };
    const color = colorMap[type] || colors.reset;
    console.log(`${color}${message}${colors.reset}`);
}

function checkFileExists(filePath, description) {
    if (fs.existsSync(filePath)) {
        log(`✅ ${description}`, 'pass');
        return true;
    } else {
        log(`❌ ${description} NOT FOUND: ${filePath}`, 'fail');
        return false;
    }
}

function checkJavaScriptSyntax(filePath, description) {
    try {
        const code = fs.readFileSync(filePath, 'utf8');
        // Basic syntax check - just try to parse as module
        new Function(code);
        log(`✅ ${description} - syntax valid`, 'pass');
        return true;
    } catch (e) {
        log(`❌ ${description} - syntax error: ${e.message}`, 'fail');
        return false;
    }
}

function checkAPICompatibility() {
    log('\n📋 Checking API Compatibility...', 'info');
    
    try {
        // Read Python file
        const pythonPath = path.join(__dirname, 'hologram_processing.py');
        const pythonCode = fs.readFileSync(pythonPath, 'utf8');
        
        // Read JavaScript fallback
        const jsPath = path.join(__dirname, 'js', 'hologram_processing_fallback.js');
        const jsCode = fs.readFileSync(jsPath, 'utf8');
        
        // Extract function names from Python
        const pythonFunctions = [
            'process_image_for_hologram',
            'toggle_processing',
            'process_single_frame',
            'toggle_debug_mode',
            'update_parameters'
        ];
        
        // Check if JavaScript has corresponding methods
        let allFound = true;
        for (const funcName of pythonFunctions) {
            // Convert snake_case to camelCase for JavaScript
            const jsFuncName = funcName.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
            
            if (jsCode.includes(jsFuncName)) {
                log(`  ✅ ${funcName} → ${jsFuncName}`, 'pass');
            } else {
                log(`  ❌ Missing: ${funcName} → ${jsFuncName}`, 'fail');
                allFound = false;
            }
        }
        
        return allFound;
    } catch (e) {
        log(`❌ Error checking API compatibility: ${e.message}`, 'fail');
        return false;
    }
}

function checkDetectionLogic() {
    log('\n🔍 Checking Detection Logic...', 'info');
    
    try {
        const loaderPath = path.join(__dirname, 'js', 'pyscript_fallback_loader.js');
        const loaderCode = fs.readFileSync(loaderPath, 'utf8');
        
        const checks = [
            { pattern: /iPad.*iPhone.*iPod/i, desc: 'iOS device detection' },
            { pattern: /WebAssembly/i, desc: 'WebAssembly support check' },
            { pattern: /SharedArrayBuffer/i, desc: 'SharedArrayBuffer check' },
            { pattern: /navigator\.maxTouchPoints/i, desc: 'iPad Pro detection' },
            { pattern: /pyScriptTimeout|pyScriptInitTimer.*setTimeout/is, desc: 'PyScript initialization timeout' }
        ];
        
        let allFound = true;
        for (const check of checks) {
            if (check.pattern.test(loaderCode)) {
                log(`  ✅ ${check.desc}`, 'pass');
            } else {
                log(`  ❌ Missing: ${check.desc}`, 'fail');
                allFound = false;
            }
        }
        
        return allFound;
    } catch (e) {
        log(`❌ Error checking detection logic: ${e.message}`, 'fail');
        return false;
    }
}

function checkHTMLIntegration() {
    log('\n🌐 Checking HTML Integration...', 'info');
    
    const htmlFiles = [
        { path: 'index.html', desc: 'Main hologram page' },
        { path: 'index_offaxis.html', desc: 'Off-axis hologram page' }
    ];
    
    let allGood = true;
    for (const file of htmlFiles) {
        const filePath = path.join(__dirname, file.path);
        
        if (!fs.existsSync(filePath)) {
            log(`  ⚠️  ${file.desc} not found`, 'warn');
            continue;
        }
        
        const htmlCode = fs.readFileSync(filePath, 'utf8');
        
        if (htmlCode.includes('pyscript_fallback_loader.js')) {
            log(`  ✅ ${file.desc} includes fallback loader`, 'pass');
        } else {
            log(`  ❌ ${file.desc} missing fallback loader`, 'fail');
            allGood = false;
        }
    }
    
    return allGood;
}

function checkDocumentation() {
    log('\n📚 Checking Documentation...', 'info');
    
    const docPath = path.join(__dirname, 'PYSCRIPT_FALLBACK.md');
    
    if (fs.existsSync(docPath)) {
        const docContent = fs.readFileSync(docPath, 'utf8');
        
        const sections = [
            'Overview',
            'Problem',
            'Solution',
            'How It Works',
            'Limitations',
            'API Compatibility'
        ];
        
        let allFound = true;
        for (const section of sections) {
            if (docContent.toLowerCase().includes(section.toLowerCase())) {
                log(`  ✅ Section: ${section}`, 'pass');
            } else {
                log(`  ⚠️  Section missing or not found: ${section}`, 'warn');
                allFound = false;
            }
        }
        
        return allFound;
    } else {
        log('  ❌ Documentation file not found', 'fail');
        return false;
    }
}

// Main validation
function runValidation() {
    log('═══════════════════════════════════════════', 'blue');
    log('  PyScript Fallback Validation', 'blue');
    log('═══════════════════════════════════════════\n', 'blue');
    
    const tests = [];
    
    // File existence checks
    log('📁 Checking File Existence...', 'info');
    tests.push(checkFileExists(
        path.join(__dirname, 'js', 'pyscript_fallback_loader.js'),
        'Fallback loader script'
    ));
    tests.push(checkFileExists(
        path.join(__dirname, 'js', 'hologram_processing_fallback.js'),
        'Fallback processing script'
    ));
    tests.push(checkFileExists(
        path.join(__dirname, 'PYSCRIPT_FALLBACK.md'),
        'Documentation file'
    ));
    tests.push(checkFileExists(
        path.join(__dirname, 'test_fallback.html'),
        'Test page'
    ));
    
    // Syntax checks
    log('\n🔧 Checking JavaScript Syntax...', 'info');
    tests.push(checkJavaScriptSyntax(
        path.join(__dirname, 'js', 'pyscript_fallback_loader.js'),
        'Fallback loader'
    ));
    tests.push(checkJavaScriptSyntax(
        path.join(__dirname, 'js', 'hologram_processing_fallback.js'),
        'Fallback processor'
    ));
    
    // API compatibility
    tests.push(checkAPICompatibility());
    
    // Detection logic
    tests.push(checkDetectionLogic());
    
    // HTML integration
    tests.push(checkHTMLIntegration());
    
    // Documentation
    tests.push(checkDocumentation());
    
    // Summary
    log('\n═══════════════════════════════════════════', 'blue');
    const passed = tests.filter(t => t).length;
    const total = tests.length;
    const percentage = Math.round((passed / total) * 100);
    
    if (percentage === 100) {
        log(`✅ All tests passed! (${passed}/${total})`, 'pass');
    } else if (percentage >= 80) {
        log(`⚠️  Most tests passed: ${passed}/${total} (${percentage}%)`, 'warn');
    } else {
        log(`❌ Some tests failed: ${passed}/${total} (${percentage}%)`, 'fail');
    }
    log('═══════════════════════════════════════════\n', 'blue');
    
    return percentage === 100;
}

// Run the validation
const success = runValidation();
process.exit(success ? 0 : 1);
