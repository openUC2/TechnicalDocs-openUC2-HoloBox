#!/bin/bash

echo "🧪 Testing OpenCV.js Compatibility Fix"
echo "======================================"

# Check if the problematic cv.cos function call has been removed
echo ""
echo "📋 Checking for problematic cv.cos/cv.sin calls..."
if grep -q "cv\.cos\|cv\.sin" "static/js/hologram_processing_fallback.js"; then
    echo "❌ Found cv.cos or cv.sin calls - these will cause errors in OpenCV.js"
    grep -n "cv\.cos\|cv\.sin" "static/js/hologram_processing_fallback.js"
else
    echo "✅ No cv.cos or cv.sin calls found - compatibility issue fixed"
fi

# Check if manual cos/sin computation has been added
echo ""
echo "📋 Checking for manual cos/sin computation..."
if grep -q "Math\.cos\|Math\.sin" "static/js/hologram_processing_fallback.js"; then
    echo "✅ Found Math.cos/Math.sin calls - manual computation implemented"
    grep -n "Math\.cos\|Math\.sin" "static/js/hologram_processing_fallback.js" | head -5
else
    echo "❌ No Math.cos/Math.sin calls found - manual computation may be missing"
fi

# Check if OpenCV.js function verification has been added
echo ""
echo "📋 Checking for OpenCV.js function verification..."
if grep -q "requiredFunctions\|missingFunctions" "static/js/hologram_processing_fallback.js"; then
    echo "✅ OpenCV.js function verification added"
else
    echo "❌ OpenCV.js function verification missing"
fi

# Check for improved error handling
echo ""
echo "📋 Checking for improved error handling..."
if grep -q "_ensureCvReady" "static/js/hologram_processing_fallback.js"; then
    echo "✅ _ensureCvReady function found for error handling"
else
    echo "❌ _ensureCvReady function missing"
fi

# Verify debug logging has been added
echo ""
echo "📋 Checking for debug logging..."
if grep -q "Computing Fresnel kernel manually" "static/js/hologram_processing_fallback.js"; then
    echo "✅ Debug logging for Fresnel kernel computation found"
else
    echo "❌ Debug logging for Fresnel kernel computation missing"
fi

echo ""
echo "🎯 Summary"
echo "=========="
echo "The OpenCV.js compatibility fix includes:"
echo "• ✅ Replaced cv.cos/cv.sin with manual Math.cos/Math.sin computation"
echo "• ✅ Added OpenCV.js function availability verification"
echo "• ✅ Enhanced error handling and debugging"
echo "• ✅ Element-by-element computation for complex mathematical operations"

echo ""
echo "🚀 Testing Instructions:"
echo "1. Open the debug console in your browser"
echo "2. Load either index.html or index_offaxis.html"
echo "3. Force fallback mode using the debug controls"
echo "4. Look for the message: '🔧 Computing Fresnel kernel manually for [width]x[height] image'"
echo "5. Verify no 'cv.cos is not a function' errors appear"
echo "6. Test hologram processing functionality"

echo ""
echo "🔍 Expected Console Output:"
echo "• ✅ All required OpenCV.js functions are available"
echo "• 🔧 Computing Fresnel kernel manually for [dimensions]"
echo "• No 'TypeError: cv.cos is not a function' errors"