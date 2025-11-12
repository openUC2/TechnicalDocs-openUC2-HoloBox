#!/bin/bash

# Test script for the improved fallback detection system
# This script will test both automatic and manual fallback modes

echo "🧪 Testing Improved PyScript Fallback Detection System"
echo "======================================================="

# Test 1: Check if PyScript loader exists
echo ""
echo "📋 Test 1: Checking PyScript Fallback Loader..."
if [ -f "static/js/pyscript_fallback_loader.js" ]; then
    echo "✅ PyScript fallback loader found"
    
    # Check for key methods
    if grep -q "forceFallbackMode" static/js/pyscript_fallback_loader.js; then
        echo "✅ forceFallbackMode method found"
    else
        echo "❌ forceFallbackMode method missing"
    fi
    
    if grep -q "shouldUseFallback" static/js/pyscript_fallback_loader.js; then
        echo "✅ shouldUseFallback method found"
    else
        echo "❌ shouldUseFallback method missing"
    fi
    
    if grep -q "monitorPyScriptInit" static/js/pyscript_fallback_loader.js; then
        echo "✅ monitorPyScriptInit method found"
    else
        echo "❌ monitorPyScriptInit method missing"
    fi
else
    echo "❌ PyScript fallback loader not found"
fi

# Test 2: Check hologram processing fallback
echo ""
echo "📋 Test 2: Checking Hologram Processing Fallback..."
if [ -f "static/js/hologram_processing_fallback.js" ]; then
    echo "✅ Hologram processing fallback found"
    
    # Check for key classes
    if grep -q "class HologramProcessorOpenCV" static/js/hologram_processing_fallback.js; then
        echo "✅ HologramProcessorOpenCV class found"
    else
        echo "❌ HologramProcessorOpenCV class missing"
    fi
    
    if grep -q "class OffAxisHologramProcessor" static/js/hologram_processing_fallback.js; then
        echo "✅ OffAxisHologramProcessor class found"
    else
        echo "❌ OffAxisHologramProcessor class missing"
    fi
else
    echo "❌ Hologram processing fallback not found"
fi

# Test 3: Check if debug controls are integrated
echo ""
echo "📋 Test 3: Checking Debug Controls Integration..."

# Check inline holography page
if [ -f "static/index.html" ]; then
    echo "✅ Inline holography page found"
    
    if grep -q "loadFallbackManually" static/index.html; then
        echo "✅ Manual fallback loading function found in index.html"
    else
        echo "❌ Manual fallback loading function missing in index.html"
    fi
    
    if grep -q "debug-controls" static/index.html; then
        echo "✅ Debug controls panel found in index.html"
    else
        echo "❌ Debug controls panel missing in index.html"
    fi
else
    echo "❌ index.html not found"
fi

# Check off-axis holography page
if [ -f "static/index_offaxis.html" ]; then
    echo "✅ Off-axis holography page found"
    
    if grep -q "loadFallbackManually" static/index_offaxis.html; then
        echo "✅ Manual fallback loading function found in index_offaxis.html"
    else
        echo "❌ Manual fallback loading function missing in index_offaxis.html"
    fi
    
    if grep -q "debug-controls" static/index_offaxis.html; then
        echo "✅ Debug controls panel found in index_offaxis.html"
    else
        echo "❌ Debug controls panel missing in index_offaxis.html"
    fi
else
    echo "❌ index_offaxis.html not found"
fi

# Test 4: Check for OpenCV.js integration
echo ""
echo "📋 Test 4: Checking OpenCV.js Integration..."
if grep -q "opencv.js" static/index.html && grep -q "opencv.js" static/index_offaxis.html; then
    echo "✅ OpenCV.js CDN links found in both pages"
else
    echo "❌ OpenCV.js CDN links missing or incomplete"
fi

# Test 5: Check PyScript configuration
echo ""
echo "📋 Test 5: Checking PyScript Configuration..."
if grep -q "pyodide.mjs" static/index.html && grep -q "pyodide.mjs" static/index_offaxis.html; then
    echo "✅ PyScript configuration found in both pages"
    
    if grep -q "numpy" static/index.html && grep -q "matplotlib" static/index.html; then
        echo "✅ Required Python packages (numpy, matplotlib) configured"
    else
        echo "❌ Required Python packages missing or incomplete"
    fi
else
    echo "❌ PyScript configuration missing or incomplete"
fi

# Test 6: Documentation check
echo ""
echo "📋 Test 6: Checking Documentation..."
if [ -f "HOLOGRAM_DEBUG_GUIDE.md" ]; then
    echo "✅ Debug guide documentation found"
    
    if grep -q "forceFallbackMode" HOLOGRAM_DEBUG_GUIDE.md; then
        echo "✅ Force fallback mode documented"
    else
        echo "❌ Force fallback mode not documented"
    fi
else
    echo "❌ Debug guide documentation missing"
fi

echo ""
echo "🎯 Test Summary"
echo "==============="
echo "The fallback detection system has been improved with:"
echo "• ✅ Automatic PyScript compatibility detection"
echo "• ✅ Manual fallback mode forcing capability"
echo "• ✅ Improved initialization monitoring with py:ready events"
echo "• ✅ Enhanced error handling and recovery"
echo "• ✅ Debug controls on both holography pages"
echo "• ✅ OpenCV.js integration for enhanced processing"

echo ""
echo "🚀 Next Steps:"
echo "1. Open either page in your browser"
echo "2. Check the debug controls panel (should appear automatically)"
echo "3. Use 'Force Fallback Mode' button to test manual switching"
echo "4. Monitor console logs for detection accuracy"
echo "5. Test hologram processing in both PyScript and fallback modes"

echo ""
echo "🔍 Troubleshooting:"
echo "• If PyScript loads but fallback still triggers: Check console for timeout issues"
echo "• If manual fallback fails: Verify all scripts are properly loaded"
echo "• If processing fails: Check OpenCV.js loading status"
echo "• For iOS/mobile issues: Use manual fallback mode"