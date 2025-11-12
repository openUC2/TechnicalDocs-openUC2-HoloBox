#!/bin/bash

# Test script for HoloBox Debug Integration (Both Inline and Off-Axis)
# This script helps verify that all components are properly integrated

echo "🧪 HoloBox Debug Integration Test (Inline + Off-Axis)"
echo "======================================================"

# Check if main files exist
echo "📁 Checking required files..."

files_to_check=(
    "index.html"
    "index_offaxis.html"
    "js/pyscript_fallback_loader.js"
    "js/hologram_processing_fallback.js"
    "offaxis_processing.py"
    "hologram_processing.py"
    "camera_controls.js"
)

all_files_exist=true

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - EXISTS"
    else
        echo "❌ $file - MISSING"
        all_files_exist=false
    fi
done

echo ""

# Check for key functions and classes in files
echo "🔍 Checking key components..."

if [ -f "js/hologram_processing_fallback.js" ]; then
    if grep -q "class OffAxisHologramProcessor" js/hologram_processing_fallback.js; then
        echo "✅ OffAxisHologramProcessor class found"
    else
        echo "❌ OffAxisHologramProcessor class missing"
    fi
    
    if grep -q "class HologramProcessorOpenCV" js/hologram_processing_fallback.js; then
        echo "✅ HologramProcessorOpenCV class found"
    else
        echo "❌ HologramProcessorOpenCV class missing"
    fi
    
    if grep -q "window.OffAxisHologramProcessor" js/hologram_processing_fallback.js; then
        echo "✅ OffAxisHologramProcessor exported to window"
    else
        echo "❌ OffAxisHologramProcessor not exported"
    fi
fi

if [ -f "index.html" ]; then
    if grep -q "force-fallback-mode" index.html; then
        echo "✅ Debug controls found in index.html (Inline)"
    else
        echo "❌ Debug controls missing in index.html (Inline)"
    fi
    
    if grep -q "initializeDebugControls" index.html; then
        echo "✅ Debug initialization function found in index.html"
    else
        echo "❌ Debug initialization function missing in index.html"
    fi
fi

if [ -f "index_offaxis.html" ]; then
    if grep -q "force-fallback-mode" index_offaxis.html; then
        echo "✅ Debug controls found in index_offaxis.html (Off-Axis)"
    else
        echo "❌ Debug controls missing in index_offaxis.html (Off-Axis)"
    fi
    
    if grep -q "initializeDebugControls" index_offaxis.html; then
        echo "✅ Debug initialization function found in index_offaxis.html"
    else
        echo "❌ Debug initialization function missing in index_offaxis.html"
    fi
fi

echo ""

# Check for potential issues
echo "⚠️  Checking for potential issues..."

if [ -f "js/pyscript_fallback_loader.js" ]; then
    if grep -q "HologramProcessorOpenCV" js/pyscript_fallback_loader.js; then
        echo "✅ Fallback loader supports HologramProcessorOpenCV"
    else
        echo "⚠️  Fallback loader might not support HologramProcessorOpenCV"
    fi
    
    if grep -q "isIOS = 1" js/pyscript_fallback_loader.js; then
        echo "🔧 Debug mode active (isIOS = 1) - fallback forced"
    else
        echo "ℹ️  Normal mode (isIOS detection enabled)"
    fi
fi

echo ""

# Provide testing instructions
echo "🚀 Testing Instructions:"
echo ""
echo "📄 For Inline Holography (index.html):"
echo "1. Open index.html in a web browser"
echo "2. Look for the '🔧 Debug & Testing Controls' panel"
echo "3. Check 'Force JavaScript Fallback Mode'"
echo "4. Check 'Enable OpenCV.js for Enhanced Processing'"
echo "5. Click 'Test Current Mode' to verify functionality"
echo "6. Test basic hologram processing with camera stream"
echo ""
echo "📄 For Off-Axis Holography (index_offaxis.html):"
echo "1. Open index_offaxis.html in a web browser"
echo "2. Look for the '🔧 Debug & Testing Controls' panel"
echo "3. Check 'Force JavaScript Fallback Mode'"
echo "4. Check 'Enable OpenCV.js for Full Processing'"
echo "5. Click 'Test Current Mode' to verify functionality"
echo "6. Test ROI selection and four-panel reconstruction"
echo ""
echo "🔍 Common checks for both:"
echo "- Check browser console for detailed logs"
echo "- Verify processing mode status indicator"
echo "- Test camera stream functionality first"

echo ""

if [ "$all_files_exist" = true ]; then
    echo "✅ All required files are present!"
    echo "🎯 Integration appears complete. Ready for testing!"
else
    echo "❌ Some files are missing. Please check the file paths."
    echo "🔧 You may need to adjust file paths or ensure all files are in the correct location."
fi

echo ""
echo "📖 For detailed testing guide, see HOLOGRAM_DEBUG_GUIDE.md"
echo "🔧 Current debug setting: Force fallback mode is ENABLED (isIOS = 1)"
echo "🌐 To test normal operation, change 'isIOS = 1' to 'isIOS = this.isIOSDevice()'"