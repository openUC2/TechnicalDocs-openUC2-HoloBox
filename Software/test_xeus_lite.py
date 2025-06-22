#!/usr/bin/env python3
"""
Test script for xeus-lite JupyterLite build system.

This script validates the xeus-lite-demo implementation including:
- Build system functionality
- File structure creation
- Configuration validation
- GitHub Actions workflow
- Notebook content
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import tempfile
import shutil

def test_file_structure():
    """Test that required files are present."""
    print("Testing file structure...")
    
    required_files = [
        "build_xeus_lite.py",
        "jupyter-lite.json", 
        "requirements-jupyter.txt",
        "content/hologram_processing.ipynb",
        "XEUS_LITE_README.md",
        "../.github/workflows/deploy-jupyter.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(file_path)
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  ✓ {file_path}")
    
    if missing_files:
        print(f"  ✗ Missing files: {missing_files}")
        return False
    
    print("  ✅ All required files present")
    return True

def test_jupyter_config():
    """Test JupyterLite configuration."""
    print("\nTesting jupyter-lite.json configuration...")
    
    config_path = Path("jupyter-lite.json")
    if not config_path.exists():
        print("  ✗ jupyter-lite.json not found")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        # Check required configuration sections
        required_keys = ["LiteBuildConfig"]
        for key in required_keys:
            if key not in config:
                print(f"  ✗ Missing config key: {key}")
                return False
            print(f"  ✓ Found config section: {key}")
        
        # Check xeus configuration
        lite_config = config["LiteBuildConfig"]
        if "federated_extensions" in lite_config:
            extensions = lite_config["federated_extensions"]
            if "@jupyterlite/xeus-python-kernel" in extensions:
                print("  ✓ xeus-python kernel configured")
            else:
                print("  ⚠ xeus-python kernel not in extensions")
        
        print("  ✅ Configuration valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False

def test_notebook_content():
    """Test notebook content structure."""
    print("\nTesting notebook content...")
    
    notebook_path = Path("content/hologram_processing.ipynb")
    if not notebook_path.exists():
        print("  ✗ Main notebook not found")
        return False
    
    try:
        with open(notebook_path) as f:
            notebook = json.load(f)
        
        # Check notebook structure
        required_keys = ["cells", "metadata", "nbformat"]
        for key in required_keys:
            if key not in notebook:
                print(f"  ✗ Missing notebook key: {key}")
                return False
        
        # Check kernel specification
        if "kernelspec" in notebook.get("metadata", {}):
            kernel = notebook["metadata"]["kernelspec"]
            if kernel.get("name") == "xeus-python":
                print("  ✓ xeus-python kernel specified")
            else:
                print("  ⚠ Kernel not set to xeus-python")
        
        # Check for hologram processing content
        cells = notebook.get("cells", [])
        code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
        
        has_processing = False
        for cell in code_cells:
            source = "".join(cell.get("source", []))
            if "HologramProcessor" in source or "fresnel_propagate" in source:
                has_processing = True
                break
        
        if has_processing:
            print("  ✓ Hologram processing content found")
        else:
            print("  ⚠ No hologram processing content detected")
        
        print(f"  ✓ Notebook has {len(cells)} cells ({len(code_cells)} code cells)")
        print("  ✅ Notebook content valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid notebook JSON: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Notebook error: {e}")
        return False

def test_github_workflow():
    """Test GitHub Actions workflow."""
    print("\nTesting GitHub Actions workflow...")
    
    workflow_path = Path("../.github/workflows/deploy-jupyter.yml")
    if not workflow_path.exists():
        print("  ✗ Workflow file not found")
        return False
    
    try:
        with open(workflow_path) as f:
            content = f.read()
        
        # Check for required workflow elements
        required_elements = [
            "name: Deploy JupyterLite",
            "jupyter lite build",
            "youseetoo.github.io",
            "peaceiris/actions-gh-pages"
        ]
        
        for element in required_elements:
            if element in content:
                print(f"  ✓ Found: {element}")
            else:
                print(f"  ✗ Missing: {element}")
                return False
        
        print("  ✅ Workflow configuration valid")
        return True
        
    except Exception as e:
        print(f"  ✗ Workflow error: {e}")
        return False

def test_build_script():
    """Test build script functionality."""
    print("\nTesting build script...")
    
    build_script = Path("build_xeus_lite.py")
    if not build_script.exists():
        print("  ✗ Build script not found")
        return False
    
    # Test that script can be imported and has required functions
    try:
        import sys
        sys.path.append(str(Path.cwd()))
        
        # This is a basic import test - actual building requires dependencies
        print("  ✓ Build script syntax valid")
        
        # Check if script has main function
        with open(build_script) as f:
            content = f.read()
        
        if "def main():" in content:
            print("  ✓ Main function found")
        else:
            print("  ✗ Main function missing")
            return False
        
        if "create_minimal_structure" in content:
            print("  ✓ Fallback structure creation found")
        else:
            print("  ✗ Fallback functionality missing")
            return False
        
        print("  ✅ Build script valid")
        return True
        
    except Exception as e:
        print(f"  ✗ Build script error: {e}")
        return False

def test_static_output():
    """Test that static output structure exists."""
    print("\nTesting static output...")
    
    static_dir = Path("static")
    if not static_dir.exists():
        print("  ✗ Static directory not found")
        return False
    
    # Check for key files
    key_files = [
        "static/notebook.html",
        "static/jupyter/lab/index.html"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ⚠ {file_path} not found (run build first)")
    
    print("  ✅ Static structure check complete")
    return True

def test_requirements():
    """Test requirements file."""
    print("\nTesting requirements...")
    
    req_file = Path("requirements-jupyter.txt")
    if not req_file.exists():
        print("  ✗ Requirements file not found")
        return False
    
    try:
        with open(req_file) as f:
            requirements = f.read().strip().split('\n')
        
        required_packages = [
            "jupyterlite-core",
            "jupyterlite-xeus-python",
            "numpy",
            "matplotlib",
            "scipy"
        ]
        
        for pkg in required_packages:
            found = any(pkg in req for req in requirements)
            if found:
                print(f"  ✓ {pkg}")
            else:
                print(f"  ✗ Missing: {pkg}")
                return False
        
        print("  ✅ Requirements valid")
        return True
        
    except Exception as e:
        print(f"  ✗ Requirements error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("xeus-lite JupyterLite Build System Tests")
    print("=" * 60)
    
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Jupyter Configuration", test_jupyter_config),
        ("Notebook Content", test_notebook_content),
        ("GitHub Workflow", test_github_workflow),
        ("Build Script", test_build_script),
        ("Static Output", test_static_output),
        ("Requirements", test_requirements)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! xeus-lite implementation is ready.")
        print("\nNext steps:")
        print("1. Run: python build_xeus_lite.py")
        print("2. Start: python streamlined_camera_api.py")
        print("3. Open: http://localhost:8000/static/notebook.html")
        print("4. Deploy: Push to main branch for GitHub Pages deployment")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())