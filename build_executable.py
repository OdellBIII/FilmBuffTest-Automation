#!/usr/bin/env python3
"""
Build script for creating the TikTok Creator executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil

def check_requirements():
    """Check if all required packages are installed"""
    import importlib.util

    # Packages that can be imported directly
    importable_packages = {
        'flask': 'flask',
        'moviepy': 'moviepy',
        'pillow': 'PIL',
        'numpy': 'numpy',
        'requests': 'requests'
    }

    missing_packages = []

    # Check importable packages
    for package_name, import_name in importable_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    # Check PyInstaller separately as it's a command-line tool
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            missing_packages.append('pyinstaller')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing_packages.append('pyinstaller')

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False

    print("✅ All required packages are installed")
    return True

def clean_build_directories():
    """Clean previous build directories"""
    directories_to_clean = ['build', 'dist', '__pycache__']

    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"🧹 Cleaning {directory}/")
            shutil.rmtree(directory)

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable with PyInstaller...")

    # Run PyInstaller with the spec file
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'tiktok-creator.spec'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Build completed successfully!")

        # Check if executable was created
        if sys.platform == 'win32':
            exe_path = 'dist/TikTokCreator.exe'
        else:
            exe_path = 'dist/TikTokCreator'

        if os.path.exists(exe_path):
            print(f"📦 Executable created: {exe_path}")

            # Get file size
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📏 File size: {size_mb:.1f} MB")

            return True
        else:
            print(f"❌ Executable not found at expected path: {exe_path}")
            return False
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

def main():
    """Main build process"""
    print("🎬 TikTok Creator - Build Script")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found. Please run this script from the project root directory.")
        sys.exit(1)

    if not os.path.exists('launcher.py'):
        print("❌ Error: launcher.py not found. Please ensure it's in the project root directory.")
        sys.exit(1)

    if not os.path.exists('tiktok-creator.spec'):
        print("❌ Error: tiktok-creator.spec not found. Please ensure it's in the project root directory.")
        sys.exit(1)

    # Step 1: Check requirements
    if not check_requirements():
        sys.exit(1)

    # Step 2: Clean previous builds
    clean_build_directories()

    # Step 3: Build executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test the executable by running it")
        print("   2. The executable will start a web server on http://localhost:8080")
        print("   3. Your browser should open automatically")
        print("\n💡 Distribution:")
        print("   - The executable is self-contained")
        print("   - No Python installation required on target machines")
        print("   - Just distribute the single executable file")
    else:
        print("\n❌ Build failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()